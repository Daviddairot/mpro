#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python update_ca.py

python manage.py import_students s.docx

python update_extra.pys