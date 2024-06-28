# update_extra.py

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

# Function to update extra scores
def update_extra_from_docx(file_path):
    # Open the Word document
    doc = Document(file_path)

    # Assuming the first table contains the data
    table = doc.tables[0]

    # Iterate through table rows (skip the header)
    for row in table.rows[1:]:
        matric_number = row.cells[0].text.strip()  # Assuming first column is matric number
        extra_score = row.cells[1].text.strip()    # Assuming second column is extra score

        try:
            extra_score = Decimal(extra_score)  # Convert extra score to Decimal
        except ValueError:
            print(f"Invalid extra score for {matric_number}: {extra_score}")
            continue

        try:
            # Find the corresponding student
            student = Student.objects.get(matric_number=matric_number)

            # Get or create the grade object
            grade, created = Grade.objects.get_or_create(student=student)

            # Update extra score
            grade.extra = extra_score

            # Convert other Decimal fields if necessary
            score = Decimal(grade.score)
            ca = Decimal(grade.ca)

            # Update total
            grade.total = score + ca + extra_score

            grade.save()
            print(f"Updated extra for {matric_number}: {extra_score}")
        except ObjectDoesNotExist:
            print(f"Student with matric number {matric_number} does not exist.")
        except Exception as e:
            print(f"Error updating {matric_number}: {e}")

if __name__ == "__main__":
    # Path to your Word document
    file_path = 'extra.docx'

    # Update extra scores
    update_extra_from_docx(file_path)
