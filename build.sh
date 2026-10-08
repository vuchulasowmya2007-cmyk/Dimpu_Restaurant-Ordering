#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "--- Installing dependencies ---"
pip install -r requirements.txt

echo "--- Collecting static files ---"
python manage.py collectstatic --no-input

echo "--- Running migrations ---"
python manage.py migrate

echo "--- Setting up superuser ---"
python create_superuser.py

echo "--- Seeding restaurant sample data ---"
python manage.py seed_data

echo "--- Build completed successfully ---"
