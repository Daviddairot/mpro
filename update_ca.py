# update_ca.py

import os
import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from docx import Document
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mpro.settings')
django.setup()

from mapp.models import Grade, Student

# Function to update CA scores
def update_ca_from_docx(file_path):
    # Open the Word document
    doc = Document(file_path)

    # Assuming the first table contains the data
    table = doc.tables[0]

    # Iterate through table rows (skip the header)
    for row in table.rows[1:]:
        matric_number = row.cells[0].text.strip()  # Assuming first column is matric number
        ca_score = row.cells[1].text.strip()       # Assuming second column is CA score

        try:
            ca_score = Decimal(ca_score)  # Convert CA score to Decimal
        except ValueError:
            print(f"Invalid CA score for {matric_number}: {ca_score}")
            continue

        try:
            # Find the corresponding student
            student = Student.objects.get(matric_number=matric_number)

            # Get or create the grade object
            grade, created = Grade.objects.get_or_create(student=student)

            # Update CA score
            grade.ca = ca_score

            # Convert other Decimal fields if necessary
            score = Decimal(grade.score)
            extra = Decimal(grade.extra)

            # Update total
            grade.total = score + ca_score + extra

            grade.save()
            print(f"Updated CA for {matric_number}: {ca_score}")
        except ObjectDoesNotExist:
            print(f"Student with matric number {matric_number} does not exist.")
        except Exception as e:
            print(f"Error updating {matric_number}: {e}")

if __name__ == "__main__":
    # Path to your Word document
    file_path = 'ca.docx'

    # Update CA scores
    update_ca_from_docx(file_path)
