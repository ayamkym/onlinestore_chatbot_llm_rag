#!/bin/bash
set -e

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Install dependencies
pip install -r requirements.txt

# Check if manage.py exists
if [ ! -f manage.py ]; then
    echo "Error: manage.py not found!"
    exit 1
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Make migrations (if there are new changes)
echo "Making migrations..."
python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
python manage.py migrate

echo "Deployment successful!"
