# Deployment Guide for Criminal Detection System on Render

## Prerequisites
1. A Render account (https://render.com)
2. A GitHub/GitLab account to host your code

## Steps to Deploy

### 1. Prepare Your Code for Deployment
1. Ensure you have the following files in your repository:
   - `render.yaml` (already created)
   - `requirements.txt` (updated with deployment dependencies)
   - Updated `settings.py` (configured for production)

2. Commit all changes to your repository:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

### 2. Deploy to Render
1. Go to https://dashboard.render.com
2. Click "New" and select "Web Service"
3. Connect your GitHub/GitLab account
4. Select your repository
5. Configure the service:
   - Name: criminal-detection-system
   - Region: Choose the closest region to your users
   - Branch: main
   - Root Directory: Leave empty (root of repository)
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python manage.py migrate && python manage.py collectstatic --noinput && gunicorn criminal_detection_system.wsgi:application`
   - Auto Deploy: Yes (recommended)

6. Add Environment Variables:
   - `SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: False
   - `ALLOWED_HOSTS`: your-render-url.onrender.com,localhost,127.0.0.1
   - `DATABASE_URL`: (Render will automatically provide this for PostgreSQL)

7. Click "Create Web Service"

### 3. Configure PostgreSQL Database
1. In the Render dashboard, click "New" and select "PostgreSQL"
2. Configure the database:
   - Name: criminal-detection-db
   - Region: Same as your web service
   - Plan: Free (for testing) or appropriate plan for production
3. Once created, Render will automatically provide the DATABASE_URL environment variable to your web service

### 4. Run Initial Setup
1. After deployment, access your web service's shell in the Render dashboard
2. Run the following commands to set up the database and populate initial data:
   ```bash
   python manage.py migrate
   python manage.py populate_criminals
   python manage.py createsuperuser
   ```

### 5. Access Your Application
1. Your application will be available at: https://your-service-name.onrender.com
2. The police dashboard will be at: https://your-service-name.onrender.com/police/
3. The admin panel will be at: https://your-service-name.onrender.com/admin/

## Environment Variables Required

| Variable | Description | Example Value |
|----------|-------------|---------------|
| SECRET_KEY | Django secret key (generate a secure one) | your-very-long-secret-key-here |
| DEBUG | Django debug mode | False |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts | your-app.onrender.com,localhost,127.0.0.1 |
| DATABASE_URL | PostgreSQL database URL | (automatically set by Render) |

## Troubleshooting

### Common Issues
1. **Application fails to start**
   - Check logs in Render dashboard
   - Ensure all environment variables are set correctly
   - Verify requirements.txt includes all necessary packages

2. **Static files not loading**
   - Ensure `whitenoise` is properly configured in settings.py
   - Check that `collectstatic` runs during deployment

3. **Database connection errors**
   - Verify DATABASE_URL environment variable is set
   - Ensure PostgreSQL database is provisioned and running

4. **Permission denied errors with media files**
   - Render's filesystem is read-only except for specific directories
   - Media files should be stored in the `media` directory which is handled correctly in settings

### Checking Logs
1. Go to your web service in the Render dashboard
2. Click on "Logs" to view real-time logs
3. Look for any error messages or warnings

## Scaling Considerations

1. **Free Tier Limitations**
   - Web services on the free tier will spin down after 15 minutes of inactivity
   - This can cause slow initial load times
   - Consider upgrading to a paid plan for production use

2. **Performance Optimization**
   - Use a CDN for static files
   - Optimize database queries
   - Consider caching for frequently accessed data

3. **Security**
   - Always use environment variables for sensitive data
   - Regularly update dependencies
   - Use HTTPS (Render provides this automatically)

## Updating Your Application

1. Make changes to your code
2. Commit and push to your repository
3. Render will automatically deploy the new version (if auto-deploy is enabled)
4. For manual deployment, click "Manual Deploy" in the Render dashboard