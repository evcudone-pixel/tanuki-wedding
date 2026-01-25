#!/usr/bin/env python3
"""
Image optimization script for wedding site.
Creates thumbnail and medium versions of photos for faster loading.
"""

from PIL import Image
import os

PHOTOS_DIR = 'photos'
THUMBNAILS_DIR = 'photos/thumbnails'
MEDIUM_DIR = 'photos/medium'

THUMBNAIL_WIDTH = 600
MEDIUM_WIDTH = 1600
JPEG_QUALITY = 85


def optimize_images():
    # Create output directories
    os.makedirs(THUMBNAILS_DIR, exist_ok=True)
    os.makedirs(MEDIUM_DIR, exist_ok=True)

    # Get all jpg files in photos directory (excluding subdirectories)
    photos = [f for f in os.listdir(PHOTOS_DIR)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))
              and os.path.isfile(os.path.join(PHOTOS_DIR, f))]

    print(f"Found {len(photos)} images to optimize...")

    for filename in photos:
        filepath = os.path.join(PHOTOS_DIR, filename)

        try:
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # Create thumbnail
                thumb_path = os.path.join(THUMBNAILS_DIR, filename)
                if not os.path.exists(thumb_path):
                    ratio = THUMBNAIL_WIDTH / img.width
                    thumb_height = int(img.height * ratio)
                    thumb = img.resize((THUMBNAIL_WIDTH, thumb_height), Image.LANCZOS)
                    thumb.save(thumb_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
                    thumb_size = os.path.getsize(thumb_path) / 1024
                    print(f"  Thumbnail: {filename} -> {thumb_size:.1f}KB")

                # Create medium version
                medium_path = os.path.join(MEDIUM_DIR, filename)
                if not os.path.exists(medium_path):
                    ratio = MEDIUM_WIDTH / img.width
                    medium_height = int(img.height * ratio)
                    medium = img.resize((MEDIUM_WIDTH, medium_height), Image.LANCZOS)
                    medium.save(medium_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
                    medium_size = os.path.getsize(medium_path) / 1024
                    print(f"  Medium: {filename} -> {medium_size:.1f}KB")

        except Exception as e:
            print(f"  Error processing {filename}: {e}")

    print("\nOptimization complete!")

    # Show total sizes
    thumb_total = sum(os.path.getsize(os.path.join(THUMBNAILS_DIR, f))
                      for f in os.listdir(THUMBNAILS_DIR)) / (1024 * 1024)
    medium_total = sum(os.path.getsize(os.path.join(MEDIUM_DIR, f))
                       for f in os.listdir(MEDIUM_DIR)) / (1024 * 1024)
    print(f"Thumbnails total: {thumb_total:.1f}MB")
    print(f"Medium total: {medium_total:.1f}MB")


if __name__ == '__main__':
    optimize_images()
