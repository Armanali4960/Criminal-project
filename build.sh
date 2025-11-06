#!/usr/bin/env bash
# Exit on error
set -o errexit

# Display Python version being used
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Check if we have the correct Python version
PYTHON_VERSION_OUTPUT=$(python --version)
if [[ $PYTHON_VERSION_OUTPUT != *"3.10.15"* ]]; then
    echo "Warning: Expected Python 3.10.15, but found $PYTHON_VERSION_OUTPUT"
fi

# Upgrade pip
pip install --upgrade pip

# Install build dependencies first
pip install "setuptools==69.5.1" "wheel==0.43.0" "build==1.2.1"

# Install numpy first (required by opencv-python)
pip install "numpy==1.24.3"

# Install opencv-python with no cache to avoid potential issues
pip install --no-cache-dir "opencv-python==4.8.0.74"

# Install remaining dependencies
pip install "Django==5.1"
pip install "Pillow==10.0.0"
pip install "gunicorn==21.2.0"
pip install "whitenoise==6.5.0"
pip install "dj-database-url==2.1.0"
pip install "psycopg2-binary==2.9.7"

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate