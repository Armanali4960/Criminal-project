# Criminal Detection System

A Django-based web application that allows citizens to upload photos for criminal detection and provides a police dashboard for monitoring.

## Features

1. **Citizen Dashboard**
   - Upload photos for criminal detection
   - Real-time face detection and matching using pixel-based comparison
   - Instant alerts when criminals are detected
   - User registration and login system
   - Camera capture functionality for live photo detection
   - Location detection and reporting

2. **Police Dashboard**
   - View all detection reports with real-time updates
   - Monitor criminal detections with detailed information
   - Access detailed report information with face coordinates
   - Statistics and analytics including dynamic accuracy rate
   - Verify detections and confirm criminal status
   - Bulk upload criminals via CSV files (backend API)
   - Admin panel integration for system management

3. **Technical Features**
   - Django backend with PostgreSQL database (Render deployment) / SQLite (local)
   - HTML/CSS/JS frontend with Bootstrap 5
   - Advanced face detection using OpenCV with multiple classifiers
   - Pixel-based image comparison for accurate matching
   - Criminal database management with photo storage
   - Responsive design for all devices
   - Real-time accuracy rate calculation
   - Automatic superuser creation for Render deployments

## Requirements

- Python 3.10.15
- Django 5.1
- OpenCV-Python 4.8.0.74
- NumPy 1.24.3
- Pillow 10.0.0
- Gunicorn 21.2.0 (for production)
- Whitenoise 6.5.0 (for static files in production)
- dj-database-url 2.1.0 (for database configuration)
- psycopg2-binary 2.9.7 (for PostgreSQL)

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

5. Initialize sample data (creates sample criminals and admin user):
   ```
   python manage.py init_data
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

## Usage

1. **Citizen Dashboard**
   - Access at: http://127.0.0.1:8000/
   - Upload photos or use camera for criminal detection
   - Register or login to save reports

2. **Police Dashboard**
   - Access at: http://127.0.0.1:8000/police/
   - View all detection reports
   - Monitor criminal detections
   - Verify detections and confirm criminal status

3. **Admin Panel**
   - Access at: http://127.0.0.1:8000/admin/
   - Default credentials: Username: admin, Password: admin
   - Manage criminals, reports, and users
   - Access advanced system configuration

4. **Bulk Criminal Upload (Backend API)**
   - Endpoint: POST /bulk-upload-criminals/
   - Requires police authentication
   - Accepts CSV files with name and description columns

## Project Structure

```
criminal_detection_system/
├── criminal_detection_system/  # Main project settings
├── detection/                  # Main app
│   ├── models.py              # Database models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   ├── management/            # Custom management commands
│   └── templates/detection/   # HTML templates
├── media/                     # Uploaded images
├── static/                    # Static files
├── staticfiles/               # Collected static files
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
- Automatic superuser creation during deployment
- PostgreSQL database configuration
- Static file serving with Whitenoise

## Models

1. **Criminal**
   - Stores information about known criminals
   - Includes name, description, and photo
   - Automatic photo generation for sample data

2. **DetectionReport**
   - Records each citizen's detection request
   - Stores uploaded images and location data
   - Tracks processing status

3. **DetectionResult**
   - Stores results of each detection
   - Links criminals to detection reports
   - Includes confidence levels and verification status
   - Tracks police verification (is_verified, is_correct)

## Views

1. **Citizen Views**
   - `index` - Citizen dashboard
   - `upload_image` - Handle image uploads with face detection
   - `camera_page` - Camera capture interface
   - `citizen_login` - User login
   - `citizen_logout` - User logout
   - `register_citizen` - User registration

2. **Police Views**
   - `police_dashboard` - Police dashboard with real-time updates
   - `get_report_details` - Detailed report information
   - `verify_detection` - Verify detection accuracy
   - `confirm_criminal_status` - Confirm if detected person is actually a criminal
   - `bulk_upload_criminals` - Bulk upload criminals via CSV (API endpoint)

3. **Management Commands**
   - `init_data` - Initialize database with sample data
   - `populate_criminals` - Add sample criminals with photos
   - `clear_database` - Clear all data from database and media files
   - `reset_password` - Reset user password
   - `fix_confidence` - Fix confidence values in database

## Recent Enhancements

1. **Pixel-Based Image Comparison**
   - Direct pixel comparison for more accurate face matching
   - Multiple comparison methods (MSE, SSIM, NCC)
   - Standardized image processing for consistency

2. **Dynamic Accuracy Rate**
   - Real-time accuracy calculation based on all detections
   - Conservative scoring to prevent artificially high rates
   - Progressive improvement as more detections are verified

3. **Enhanced Face Detection**
   - Multiple Haar cascade classifiers for better detection
   - Duplicate face removal algorithm
   - Improved preprocessing (histogram equalization, noise reduction, sharpening)

4. **Backend Bulk Upload**
   - CSV-based criminal upload via API endpoint
   - Authentication protection for police use only

5. **Automatic Deployment Setup**
   - Superuser creation during Render deployment
   - Database migration handling
   - Static file collection

## Future Enhancements

1. Integrate with real face recognition APIs
2. Add live camera detection with real-time processing
3. Implement mobile app versions
4. Add email/SMS notifications for detections
5. Include advanced geolocation services
6. Add multi-language support
7. Implement machine learning for improved accuracy
8. Add export functionality for reports and statistics