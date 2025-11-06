# Setup Guide for Criminal Detection System

## Setting Up on Another Laptop

### Prerequisites
1. Python 3.8 or higher installed
2. Git installed (optional, for cloning the repository)

### Steps to Set Up

1. **Copy the Project Files**
   - Copy the entire project folder to the new laptop

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Populate Sample Criminal Data (Optional)**
   ```bash
   python manage.py populate_criminals
   ```

6. **Create a Superuser (Optional but Recommended)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user.

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Citizen Dashboard: http://127.0.0.1:8000/
   - Police Dashboard: http://127.0.0.1:8000/police/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Creating Test Users

### For Citizen Dashboard:
1. Visit http://127.0.0.1:8000/register/ to register a new citizen account
2. Or use the admin panel to create a user and ensure "Staff status" is unchecked

### For Police Dashboard:
1. Use the admin panel to create a user and check "Staff status"
2. Or create a superuser which automatically gets staff status

## Troubleshooting

1. **Missing Haar Cascade File Error**
   - The application uses OpenCV's built-in Haar cascade files
   - Ensure opencv-python is properly installed

2. **Permission Issues with Media Files**
   - Make sure the media directory is writable
   - On Linux/macOS: `chmod 755 media/`

3. **Database Issues**
   - If you encounter database errors, try deleting `db.sqlite3` and rerunning migrations