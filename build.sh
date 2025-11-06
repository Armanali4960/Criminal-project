#!/usr/bin/env bash
# Exit on error
set -o errexit

# Ensure we're using the correct Python version
echo "Using Python version: $(python --version)"

# Upgrade pip
pip install --upgrade pip

# Install setuptools and wheel first
pip install setuptools==69.5.1 wheel==0.43.0

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate