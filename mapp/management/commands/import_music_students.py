import os
import re
import glob
from collections import defaultdict

from django.core.management.base import BaseCommand
from docx import Document

from mapp.models import Student


INSTRUMENT_KEYWORDS = [
    ("drum",     "Drum"),
    ("violin",   "Violin"),
    ("guitar",   "Guitar"),
    ("woodwind", "Woodwind"),
    ("piano",    "Piano"),
]

MATRIC_RE = re.compile(r"^EU\d{6}-\d{4}$")


def instrument_from_filename(path):
    name = os.path.basename(path).lower()
    for kw, label in INSTRUMENT_KEYWORDS:
        if kw in name:
            return label
    return None


def clean_matric(raw):
    if not raw:
        return None
    m = raw.strip().strip(".,;:").upper()
    m = re.sub(r"[\s_]+", "-", m)
    m = re.sub(r"-+", "-", m)
    if m in ("", "------", "-"):
        return None
    # Normalize "EU-NNNNNN-NNNN" -> "EUNNNNNN-NNNN"
    extra_dash = re.match(r"^EU-(\d{6}-\d{4})$", m)
    if extra_dash:
        m = "EU" + extra_dash.group(1)
    return m if MATRIC_RE.match(m) else None


def split_name(raw):
    if not raw:
        return "", ""
    n = raw.replace(",", " ").replace("\\", " ").replace(".", " ")
    n = re.sub(r"\s+", " ", n).strip()
    if not n:
        return "", ""
    parts = n.split(" ", 1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


class Command(BaseCommand):
    help = "Import students from all .docx files in a directory (instrument derived from filename)."

    def add_arguments(self, parser):
        parser.add_argument("--dir", default="music", help="Directory containing .docx files (default: music)")
        parser.add_argument("--dry-run", action="store_true", help="Parse and report only; do not write to DB")

    def handle(self, *args, **opts):
        directory = opts["dir"]
        dry_run = opts["dry_run"]

        files = sorted(glob.glob(os.path.join(directory, "*.docx")))
        if not files:
            self.stdout.write(self.style.ERROR(f"No .docx files in {directory!r}"))
            return

        parsed = []
        skipped_no_matric = 0
        skipped_bad_matric = []
        per_file = defaultdict(int)

        for fp in files:
            instrument = instrument_from_filename(fp)
            if not instrument:
                self.stdout.write(self.style.WARNING(f"Skipping {fp}: cannot infer instrument"))
                continue

            doc = Document(fp)
            for table in doc.tables:
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells]
                    if len(cells) < 3:
                        continue
                    name_cell = cells[1]
                    matric_cell = cells[2]
                    if name_cell.upper() == "NAME":
                        continue
                    if not name_cell and not matric_cell:
                        continue

                    matric = clean_matric(matric_cell)
                    if not matric:
                        if matric_cell.strip() in ("", "------"):
                            skipped_no_matric += 1
                        else:
                            skipped_bad_matric.append((fp, name_cell, matric_cell))
                        continue

                    first, last = split_name(name_cell)
                    parsed.append({
                        "matric_number": matric,
                        "first_name": first,
                        "last_name": last,
                        "instrument": instrument,
                        "source": os.path.basename(fp),
                    })
                    per_file[os.path.basename(fp)] += 1

        # Detect cross-file duplicate matrics (same student across instruments)
        by_matric = defaultdict(list)
        for r in parsed:
            by_matric[r["matric_number"]].append(r)
        conflicts = {m: rs for m, rs in by_matric.items() if len({r["instrument"] for r in rs}) > 1}

        self.stdout.write(self.style.SUCCESS("\n=== Parse summary ==="))
        for f, n in per_file.items():
            self.stdout.write(f"  {f}: {n} valid rows")
        self.stdout.write(f"  skipped (blank matric): {skipped_no_matric}")
        self.stdout.write(f"  skipped (bad matric format): {len(skipped_bad_matric)}")
        self.stdout.write(f"  cross-instrument conflicts: {len(conflicts)}")

        if skipped_bad_matric:
            self.stdout.write(self.style.WARNING("\nBad matric examples (first 10):"))
            for fp, nm, raw in skipped_bad_matric[:10]:
                self.stdout.write(f"  {os.path.basename(fp)} | {nm!r} | matric={raw!r}")

        if conflicts:
            self.stdout.write(self.style.WARNING("\nCross-instrument conflicts (last write wins):"))
            for m, rs in list(conflicts.items())[:10]:
                insts = [r["instrument"] for r in rs]
                self.stdout.write(f"  {m}: {insts}")

        # Show a preview sample
        self.stdout.write(self.style.SUCCESS("\nPreview (first 5 rows):"))
        for r in parsed[:5]:
            self.stdout.write(f"  {r}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"\nDRY RUN: would upsert {len(parsed)} unique students."))
            unique = len(by_matric)
            self.stdout.write(f"  unique matrics: {unique}")
            return

        # De-dup on matric_number so bulk_create sees one row per student
        # (last write wins, matching the user's chosen conflict policy).
        dedup = {}
        for r in parsed:
            dedup[r["matric_number"]] = r
        rows = list(dedup.values())

        objs = [
            Student(
                matric_number=r["matric_number"],
                first_name=r["first_name"],
                last_name=r["last_name"],
                instrument=r["instrument"],
            )
            for r in rows
        ]

        # Single statement upsert — avoids PgBouncer statement_timeout that kills
        # long-running atomic blocks on Supabase's transaction pooler (port 6543).
        batch = 200
        total = 0
        for i in range(0, len(objs), batch):
            chunk = objs[i:i + batch]
            Student.objects.bulk_create(
                chunk,
                update_conflicts=True,
                unique_fields=["matric_number"],
                update_fields=["first_name", "last_name", "instrument"],
            )
            total += len(chunk)
            self.stdout.write(f"  upserted {total}/{len(objs)}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDONE: upserted {len(objs)} students (deduped from {len(parsed)} parsed rows)."
        ))
