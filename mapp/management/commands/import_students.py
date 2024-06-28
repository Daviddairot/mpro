# assessments/management/commands/import_students.py
#python manage.py import_students C:\Users\DAIRO\Documents\mnew\mpro\mapp\management\commands\s.docx

import os
from django.core.management.base import BaseCommand
from mapp.models import Student
from docx import Document

class Command(BaseCommand):
    help = 'Import students from a Word document'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help=r'Path to the Word document (e.g., C:\Users\DAIRO\Documents\music\musicproject\musicapp\management\commands\s.docx)')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File '{file_path}' does not exist."))
            return

        document = Document(file_path)
        table = document.tables[0]

        rows = table.rows
        for row in rows[1:]:  # Skip the header row
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
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created student {full_name} ({matric_number})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated student {full_name} ({matric_number})"))

    def parse_name(self, full_name):
        parts = full_name.split(", ")
        if len(parts) == 2:
            return parts[0], parts[1]  # Surname, First Name
        return '', full_name  # If no comma, return empty surname and full name as first name
