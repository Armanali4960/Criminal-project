import os
from django.core.management.base import BaseCommand
from django.db import connection
from detection.models import Criminal, DetectionReport, DetectionResult

class Command(BaseCommand):
    help = 'Check database connection and initialize if needed'

    def handle(self, *args, **options):
        try:
            # Test database connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS('Database connection successful')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Database connection failed')
                )
                
            # Check if tables exist and create them if needed
            self.check_and_create_tables()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database connection error: {e}')
            )
            
    def check_and_create_tables(self):
        try:
            # Check if Criminal table exists
            criminal_count = Criminal.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'Criminal table exists with {criminal_count} records')
            )
            
            # Check if DetectionReport table exists
            report_count = DetectionReport.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'DetectionReport table exists with {report_count} records')
            )
            
            # Check if DetectionResult table exists
            result_count = DetectionResult.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'DetectionResult table exists with {result_count} records')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Tables may not exist yet: {e}')
            )
            self.stdout.write(
                self.style.WARNING('Run migrations to create tables')
            )