#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Load initial database dump
if [ -f datadump.json ]; then
    echo "Importando datos a la base de datos..."
    python manage.py loaddata datadump.json || true
fi