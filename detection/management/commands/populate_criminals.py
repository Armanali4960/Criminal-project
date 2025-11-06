import os
from django.core.management.base import BaseCommand
from django.conf import settings
from detection.models import Criminal
import cv2
import numpy as np

class Command(BaseCommand):
    help = 'Populate database with sample criminals'

    def handle(self, *args, **options):
        # Sample criminal data
        criminals_data = [
            {
                'name': 'John Doe',
                'description': 'Wanted for bank robbery and assault',
            },
            {
                'name': 'Jane Smith',
                'description': 'Wanted for identity theft and fraud',
            },
            {
                'name': 'Robert Johnson',
                'description': 'Wanted for burglary and theft',
            },
            {
                'name': 'Emily Davis',
                'description': 'Wanted for cyber crimes and hacking',
            },
            {
                'name': 'Michael Wilson',
                'description': 'Wanted for drug trafficking',
            },
            {
                'name': 'Sarah Brown',
                'description': 'Wanted for art theft',
            },
            {
                'name': 'David Miller',
                'description': 'Wanted for embezzlement',
            },
            {
                'name': 'Lisa Taylor',
                'description': 'Wanted for kidnapping',
            },
        ]

        # Create criminals
        created_count = 0
        updated_count = 0
        for data in criminals_data:
            # Check if criminal already exists
            criminal, created = Criminal.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created criminal: {criminal.name}')
            
            # Always update the photo to ensure it has a good face
            self.add_sample_photo(criminal)
            updated_count += 1
            self.stdout.write(f'Updated photo for criminal: {criminal.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} new criminals and updated {updated_count} photos. '
                f'Total criminals in database: {Criminal.objects.count()}'
            )
        )

    def add_sample_photo(self, criminal):
        """Add a sample photo for the criminal"""
        try:
            # Create a simple sample image
            img = np.ones((200, 200, 3), dtype=np.uint8) * 255  # White background
            
            # Add some basic shapes to make it look like a face
            # Face outline
            cv2.circle(img, (100, 100), 80, (0, 0, 0), 2)
            
            # Eyes
            cv2.circle(img, (70, 80), 15, (0, 0, 0), -1)
            cv2.circle(img, (130, 80), 15, (0, 0, 0), -1)
            
            # Nose
            cv2.circle(img, (100, 110), 10, (0, 0, 0), -1)
            
            # Mouth
            cv2.ellipse(img, (100, 140), (30, 15), 0, 0, 180, (0, 0, 0), 2)
            
            # Add text with criminal's name
            first_name = criminal.name.split()[0]
            cv2.putText(img, first_name, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
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
            
        except Exception as e:
            # Fallback: create a very simple image
            try:
                # Create directory if it doesn't exist
                filepath = os.path.join(settings.MEDIA_ROOT, 'criminal_photos', f"{criminal.name.replace(' ', '_').lower()}_fallback.jpg")
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Create a simple white image with text
                img = np.ones((150, 150, 3), dtype=np.uint8) * 255
                cv2.putText(img, 'CRIMINAL', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(img, criminal.name.split()[0], (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.imwrite(filepath, img)
                
                # Update criminal with photo
                criminal.photo = f'criminal_photos/{criminal.name.replace(" ", "_").lower()}_fallback.jpg'
                criminal.save()
            except Exception as e2:
                self.stdout.write(f'Could not add photo for {criminal.name}: {e2}')