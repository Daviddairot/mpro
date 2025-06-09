# assessments/management/commands/import_students.py

import os
from django.core.management.base import BaseCommand
from docx import Document
from mapp.models import Student  # Ensure correct import

class Command(BaseCommand):
    help = 'Import students from a Word document'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help=r'Path to the Word document (e.g., C:\Users\user\Documents\mpro\mapp\s.docx)'
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File '{file_path}' does not exist."))
            return

        document = Document(file_path)
        table = document.tables[0]

        for row in table.rows[1:]:
            matric_number = row.cells[0].text.strip()
            full_name = row.cells[1].text.strip()
            instrument = row.cells[2].text.strip()

            surname, first_name = self.parse_name(full_name)

            student, created = Student.objects.update_or_create(
                matric_number=matric_number,
                defaults={
                    'first_name': first_name,
                    'last_name': surname,
                    'instrument': instrument
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} student {full_name} ({matric_number})"))

    def parse_name(self, full_name):
        parts = full_name.split(", ")
        return (parts[0], parts[1]) if len(parts) == 2 else ('', full_name)
