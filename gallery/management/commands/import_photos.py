"""
Management command to import existing gallery photos from the old site.
Usage: python manage.py import_photos
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from gallery.models import GalleryPhoto


class Command(BaseCommand):
    help = 'Import existing gallery photos from public_html/images/galeria/'

    def handle(self, *args, **options):
        # Source directory (relative to manage.py)
        source_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / 'public_html' / 'images' / 'galeria'
        
        if not source_dir.exists():
            self.stderr.write(self.style.ERROR(f'Source directory not found: {source_dir}'))
            return
        
        # Create media/gallery directory if it doesn't exist
        media_gallery = Path(settings.MEDIA_ROOT) / 'gallery'
        media_gallery.mkdir(parents=True, exist_ok=True)
        
        # Get all jpg files (excluding thumbnails starting with 'min_')
        image_files = [f for f in source_dir.glob('*.jpg') if not f.name.startswith('min_')]
        
        self.stdout.write(f'Found {len(image_files)} images to import (excluding thumbnails)')
        
        imported = 0
        skipped = 0
        
        for image_path in image_files:
            filename = image_path.name.lower()
            
            # Determine category based on filename
            if 'cardio' in filename:
                category = 'cardio'
            elif 'elgym' in filename:
                category = 'elgym'
            elif 'muscu' in filename or filename.startswith('m') and filename[1].isdigit():
                category = 'musculacion'
            elif 'vest' in filename:
                category = 'vestuarios'
            elif 'fitness' in filename:
                category = 'elgym'  # Group fitness with gym
            else:
                category = 'elgym'  # Default to gym
            
            # Generate title from filename
            name_without_ext = os.path.splitext(filename)[0]
            title = name_without_ext.replace('_', ' ').replace('-', ' ').title()
            
            # Check if photo already exists
            if GalleryPhoto.objects.filter(title=title).exists():
                self.stdout.write(f'  Skipping (exists): {filename}')
                skipped += 1
                continue
            
            try:
                # Create the photo instance first
                photo = GalleryPhoto(
                    title=title,
                    caption='',
                    alt_text=f'{title} - PowerGYM',
                    category=category,
                    is_active=True,
                    sort_order=imported,
                )
                
                # Open and save the image file
                with open(image_path, 'rb') as f:
                    from django.core.files.uploadedfile import SimpleUploadedFile
                    uploaded_file = SimpleUploadedFile(
                        name=filename,
                        content=f.read(),
                        content_type='image/jpeg'
                    )
                    photo.image = uploaded_file
                    photo.save()
                
                imported += 1
                self.stdout.write(self.style.SUCCESS(f'  Imported: {filename} ({category})'))
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error importing {filename}: {e}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Import complete: {imported} imported, {skipped} skipped'))
