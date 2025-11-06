import os
from django.core.management.base import BaseCommand
from django.conf import settings
from detection.models import Criminal
import cv2
import numpy as np

class Command(BaseCommand):
    help = 'Initialize database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database with sample data...')
        
        try:
            # Ensure media directories exist
            media_root = settings.MEDIA_ROOT
            criminal_photos_dir = os.path.join(media_root, 'criminal_photos')
            os.makedirs(criminal_photos_dir, exist_ok=True)
            
            self.stdout.write(f'Media directories created: {criminal_photos_dir}')
            
            # Create sample criminals if none exist
            if Criminal.objects.count() == 0:
                self.create_sample_criminals()
            else:
                self.stdout.write('Criminals already exist in database')
                
            self.stdout.write(
                self.style.SUCCESS('Database initialization completed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database initialization failed: {e}')
            )
            
    def create_sample_criminals(self):
        """Create sample criminals with photos"""
        criminals_data = [
            {
                'name': 'Tushar Singh',
                'description': 'Wanted for cyber crimes and identity theft',
            },
            {
                'name': 'John Doe',
                'description': 'Wanted for bank robbery and assault',
            },
            {
                'name': 'Jane Smith',
                'description': 'Wanted for identity theft and fraud',
            },
        ]
        
        created_count = 0
        for data in criminals_data:
            try:
                # Create criminal
                criminal, created = Criminal.objects.get_or_create(
                    name=data['name'],
                    defaults=data
                )
                
                if created:
                    self.stdout.write(f'Created criminal: {criminal.name}')
                    created_count += 1
                    
                # Add sample photo
                self.add_sample_photo(criminal)
            except Exception as e:
                self.stdout.write(f'Could not create criminal {data["name"]}: {e}')
            
        self.stdout.write(f'Created {created_count} sample criminals')
            
    def add_sample_photo(self, criminal):
        """Add a sample photo for the criminal"""
        try:
            # Create a simple sample image
            img = np.ones((300, 300, 3), dtype=np.uint8) * 255  # White background
            
            # Draw a simple face pattern
            # Face outline
            cv2.circle(img, (150, 150), 100, (0, 0, 0), 2)
            
            # Eyes
            cv2.circle(img, (120, 130), 15, (0, 0, 0), -1)
            cv2.circle(img, (180, 130), 15, (0, 0, 0), -1)
            
            # Mouth
            cv2.ellipse(img, (150, 190), (30, 15), 0, 0, 180, (0, 0, 0), 2)
            
            # Save the image
            filename = f"{criminal.name.replace(' ', '_').lower()}_{np.random.randint(1000, 9999)}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, 'criminal_photos', filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save image
            cv2.imwrite(filepath, img)
            
            # Update criminal with photo
            criminal.photo = f'criminal_photos/{filename}'
            criminal.save()
            
            self.stdout.write(f'Added photo for criminal: {criminal.name}')
            
        except Exception as e:
            self.stdout.write(f'Could not add photo for {criminal.name}: {e}')