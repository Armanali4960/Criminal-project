# Criminal Detection System

A Django-based web application that allows citizens to upload photos for criminal detection and provides a police dashboard for monitoring.

## Features

1. **Citizen Dashboard**
   - Upload photos for criminal detection
   - Real-time face detection and matching
   - Instant alerts when criminals are detected
   - User registration and login system

2. **Police Dashboard**
   - View all detection reports
   - Monitor criminal detections
   - Access detailed report information
   - Statistics and analytics

3. **Technical Features**
   - Django backend with SQLite database
   - HTML/CSS/JS frontend with Bootstrap
   - Face detection using OpenCV
   - Criminal database management
   - Responsive design for all devices

## Requirements

- Python 3.8+
- Django 5.1
- OpenCV-Python 4.8.0.74
- NumPy 1.24.3
- Pillow 10.0.0

## Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```
   cd criminal_detection_system
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations to create the database:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. **Citizen Dashboard**
   - Access at: http://127.0.0.1:8000/
   - Upload photos for criminal detection
   - Register or login to save reports

2. **Police Dashboard**
   - Access at: http://127.0.0.1:8000/police/
   - View all detection reports
   - Monitor criminal detections

3. **Admin Panel** (if superuser created)
   - Access at: http://127.0.0.1:8000/admin/
   - Manage criminals, reports, and users

## Project Structure

```
criminal_detection_system/
├── criminal_detection_system/  # Main project settings
├── detection/                  # Main app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   └── templates/detection/   # HTML templates
├── media/                     # Uploaded images
├── static/                    # Static files
├── templates/                 # Base templates
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Setup and Deployment

### Running on Another Laptop
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions on setting up the project on another laptop.

### Deploying to Render
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions on deploying the application to Render.

## Models

1. **Criminal**
   - Stores information about known criminals
   - Includes name, description, and photo

2. **DetectionReport**
   - Records each citizen's detection request
   - Stores uploaded images and location data

3. **DetectionResult**
   - Stores results of each detection
   - Links criminals to detection reports
   - Includes confidence levels

## Views

1. **Citizen Views**
   - `index` - Citizen dashboard
   - `upload_image` - Handle image uploads
   - `citizen_login` - User login
   - `citizen_logout` - User logout
   - `register_citizen` - User registration

2. **Police Views**
   - `police_dashboard` - Police dashboard
   - `get_report_details` - Detailed report information

## Templates

1. **citizen_dashboard.html** - Main citizen interface
2. **police_dashboard.html** - Police monitoring interface
3. **login.html** - User login page
4. **register.html** - User registration page

## Future Enhancements

1. Integrate with real face recognition APIs
2. Add live camera detection
3. Implement mobile app versions
4. Add email/SMS notifications
5. Include geolocation services
6. Add multi-language support