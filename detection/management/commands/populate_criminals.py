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
            # Create a better quality sample image with a realistic face
            img = np.ones((300, 300, 3), dtype=np.uint8) * 255  # White background
            
            # Draw a more realistic face pattern
            # Face outline (ellipse)
            cv2.ellipse(img, (150, 150), (100, 120), 0, 0, 360, (0, 0, 0), 2)
            
            # Eyes
            cv2.ellipse(img, (120, 130), (20, 25), 0, 0, 360, (0, 0, 0), -1)
            cv2.ellipse(img, (180, 130), (20, 25), 0, 0, 360, (0, 0, 0), -1)
            cv2.circle(img, (120, 130), 8, (255, 255, 255), -1)
            cv2.circle(img, (180, 130), 8, (255, 255, 255), -1)
            
            # Eyebrows
            cv2.ellipse(img, (120, 110), (25, 10), 0, 0, 180, (0, 0, 0), 3)
            cv2.ellipse(img, (180, 110), (25, 10), 0, 0, 180, (0, 0, 0), 3)
            
            # Nose
            cv2.ellipse(img, (150, 150), (15, 20), 0, 0, 360, (0, 0, 0), -1)
            
            # Mouth
            cv2.ellipse(img, (150, 190), (30, 15), 0, 0, 180, (0, 0, 0), 2)
            
            # Add some facial features to make it look more realistic
            # Cheeks
            cv2.circle(img, (100, 160), 15, (200, 200, 200), -1)
            cv2.circle(img, (200, 160), 15, (200, 200, 200), -1)
            
            # Add text with criminal's name
            first_name = criminal.name.split()[0]
            cv2.putText(img, first_name, (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Save the image
            filename = f"{criminal.name.replace(' ', '_').lower()}_{np.random.randint(1000, 9999)}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, 'criminal_photos', filename)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save image with higher quality
            cv2.imwrite(filepath, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # Update criminal with photo
            criminal.photo = f'criminal_photos/{filename}'
            criminal.save()
            
        except Exception as e:
            self.stdout.write(f'Could not add photo for {criminal.name}: {e}')