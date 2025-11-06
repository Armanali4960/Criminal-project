FROM python:3.10.15-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1-mesa-glx \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install setuptools==69.5.1 wheel==0.43.0 build==1.2.1
RUN pip install numpy==1.24.3
RUN pip install --no-cache-dir opencv-python==4.8.0.74
RUN pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations
RUN python manage.py migrate --noinput

# Initialize data
RUN python manage.py init_data

# Expose port
EXPOSE $PORT

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "criminal_detection_system.wsgi:application"]