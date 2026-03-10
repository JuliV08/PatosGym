"""
Management command to ingest raw images from /media/raw_uploads/,
convert them to .webp using Pillow, and distribute them intelligently:
  - 4-5 best-quality landscape images → HeroImage (landing app)
  - All remaining images → GalleryPhoto (gallery app)

Usage:
    python manage.py load_initial_images
    python manage.py load_initial_images --source media/raw_uploads
    python manage.py load_initial_images --dry-run
    python manage.py load_initial_images --max-hero 5 --quality 88
"""

import io
import os
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management.base import BaseCommand, CommandError

from gallery.models import GalleryPhoto
from landing.models import HeroImage

# ── Extensions we accept as raw input
ACCEPTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.heic'}

# ── Keyword → GalleryPhoto.category mapping (lowercase match)
CATEGORY_KEYWORDS = {
    'vestuarios': ['vestuario', 'vestuarios', 'baño', 'bano', 'shower', 'locker'],
    'cardio':     ['cardio', 'bike', 'cinta', 'eliptica', 'elíptica', 'bici', 'spinning'],
    'musculacion':['muscu', 'pesa', 'mancuerna', 'barra', 'squat', 'press', 'rack', 'bench'],
    'transformaciones': ['transform', 'antes', 'despues', 'después', 'before', 'after'],
    'atletas':    ['atleta', 'athlete', 'competencia', 'torneo'],
}
DEFAULT_CATEGORY = 'musculacion'


def _detect_category(filename_stem: str) -> str:
    """Infer GalleryPhoto category from filename (lowercase stem)."""
    lower = filename_stem.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return DEFAULT_CATEGORY


def _title_from_stem(stem: str) -> str:
    """Generate a human-readable title from the filename stem."""
    return stem.replace('_', ' ').replace('-', ' ').title()


def _is_landscape(width: int, height: int, ratio_threshold: float = 1.2) -> bool:
    """Return True if image is significantly landscape-oriented."""
    return width > height * ratio_threshold


def _convert_to_webp(img_pil, quality: int = 85) -> io.BytesIO:
    """Convert a Pillow Image to WebP and return a BytesIO buffer."""
    buf = io.BytesIO()
    # Convert to RGB to ensure WebP compatibility (removes alpha channel issues)
    if img_pil.mode in ('RGBA', 'LA', 'P'):
        img_pil = img_pil.convert('RGBA')
        # Paste onto black background to flatten transparency
        background = __import__('PIL.Image', fromlist=['Image']).Image.new('RGB', img_pil.size, (10, 10, 10))
        background.paste(img_pil, mask=img_pil.split()[-1])
        img_pil = background
    else:
        img_pil = img_pil.convert('RGB')
    img_pil.save(buf, format='WEBP', quality=quality, method=6)
    buf.seek(0)
    return buf


class Command(BaseCommand):
    help = (
        'Ingest raw images from /media/raw_uploads/, convert to WebP, '
        'auto-distribute between HeroImage and GalleryPhoto.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='media/raw_uploads',
            help='Path to source directory (relative to BASE_DIR or absolute). Default: media/raw_uploads',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Preview what would be done without writing to the DB or disk.',
        )
        parser.add_argument(
            '--max-hero',
            type=int,
            default=5,
            help='Maximum number of images to assign as HeroImage. Default: 5',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='WebP output quality (1-100). Default: 85',
        )

    def handle(self, *args, **options):
        try:
            from PIL import Image
            try:
                import pillow_heif
                pillow_heif.register_heif_opener()
            except ImportError:
                pass # Optional HEIC support
        except ImportError:
            raise CommandError('Pillow is required. Run: pip install Pillow')

        dry_run   = options['dry_run']
        max_hero  = options['max_hero']
        quality   = options['quality']

        # ── Resolve source directory
        source_path = Path(options['source'])
        if not source_path.is_absolute():
            source_path = Path(settings.BASE_DIR) / source_path

        if not source_path.exists():
            raise CommandError(
                f'Source directory not found: {source_path}\n'
                f'Create it and place your raw images inside, then re-run.'
            )

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'\n{"─"*60}\n  PatosGym — Image Ingestion{"  [DRY RUN]" if dry_run else ""}\n{"─"*60}'
        ))
        self.stdout.write(f'  Source : {source_path}')
        self.stdout.write(f'  Quality: {quality}%   Max hero: {max_hero}')

        # ── Collect valid image files
        raw_files = [
            f for f in source_path.iterdir()
            if f.is_file() and f.suffix.lower() in ACCEPTED_EXTENSIONS
        ]

        if not raw_files:
            self.stdout.write(self.style.WARNING(
                f'\nNo images found in {source_path}. Accepted extensions: '
                + ', '.join(sorted(ACCEPTED_EXTENSIONS))
            ))
            return

        self.stdout.write(f'\n  Found {len(raw_files)} candidate file(s).\n')

        # ── Open all images and gather metadata for sorting
        image_data = []  # list of dicts
        for fpath in raw_files:
            try:
                img = Image.open(fpath)
                img.verify()          # Detect corrupt files
                img = Image.open(fpath)  # Re-open after verify (verify closes stream)
                w, h = img.size
                megapixels = (w * h) / 1_000_000
                image_data.append({
                    'path': fpath,
                    'img':  img,
                    'width': w,
                    'height': h,
                    'megapixels': megapixels,
                    'landscape': _is_landscape(w, h),
                })
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'  [SKIP] {fpath.name} — cannot open: {exc}'))

        if not image_data:
            self.stdout.write(self.style.WARNING('  No valid images to process.'))
            return

        # ── Select Hero candidates: landscape, sorted by total pixels (best quality first)
        landscape_sorted = sorted(
            [d for d in image_data if d['landscape']],
            key=lambda d: d['megapixels'],
            reverse=True,
        )
        hero_candidates  = landscape_sorted[:max_hero]
        hero_paths       = {d['path'] for d in hero_candidates}
        gallery_data     = [d for d in image_data if d['path'] not in hero_paths]

        self.stdout.write(self.style.MIGRATE_HEADING(
            f'  Hero   → {len(hero_candidates)} image(s)\n'
            f'  Gallery→ {len(gallery_data)} image(s)\n'
        ))

        hero_added    = 0
        gallery_added = 0
        skipped       = 0
        errors        = 0

        # ── Process Hero images
        self.stdout.write(self.style.MIGRATE_HEADING('── Hero Images ──'))
        for order, d in enumerate(hero_candidates):
            stem     = d['path'].stem
            webp_name = f"{stem}.webp"
            title     = _title_from_stem(stem)

            # Skip duplicates
            if HeroImage.objects.filter(titulo=title).exists():
                self.stdout.write(f'  [SKIP] {webp_name}  (already in HeroImage)')
                skipped += 1
                continue

            self.stdout.write(
                f'  [HERO] {webp_name}  {d["width"]}×{d["height"]}  '
                f'{d["megapixels"]:.1f}MP  {"landscape ✓" if d["landscape"] else "portrait"}'
            )

            if dry_run:
                continue

            try:
                buf = _convert_to_webp(d['img'], quality=quality)
                uploaded = InMemoryUploadedFile(
                    file=buf,
                    field_name='imagen',
                    name=webp_name,
                    content_type='image/webp',
                    size=buf.getbuffer().nbytes,
                    charset=None,
                )
                hero = HeroImage(
                    titulo=title,
                    orden=order,
                    activo=True,
                )
                hero.imagen = uploaded
                hero.save()
                hero_added += 1
                self.stdout.write(self.style.SUCCESS(f'        → saved (pk={hero.pk})'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'        → ERROR: {exc}'))
                errors += 1

        # ── Process Gallery images
        self.stdout.write(self.style.MIGRATE_HEADING('\n── Gallery Photos ──'))
        for order, d in enumerate(gallery_data):
            stem      = d['path'].stem
            webp_name = f"{stem}.webp"
            title     = _title_from_stem(stem)
            category  = _detect_category(stem)

            # Skip duplicates
            if GalleryPhoto.objects.filter(title=title).exists():
                self.stdout.write(f'  [SKIP] {webp_name}  (already in GalleryPhoto)')
                skipped += 1
                continue

            self.stdout.write(
                f'  [GALLERY/{category}] {webp_name}  {d["width"]}×{d["height"]}'
            )

            if dry_run:
                continue

            try:
                buf = _convert_to_webp(d['img'], quality=quality)
                uploaded = InMemoryUploadedFile(
                    file=buf,
                    field_name='image',
                    name=webp_name,
                    content_type='image/webp',
                    size=buf.getbuffer().nbytes,
                    charset=None,
                )
                photo = GalleryPhoto(
                    title=title,
                    caption='',
                    alt_text=f'{title} — PatosGYM',
                    category=category,
                    is_active=True,
                    sort_order=order,
                )
                photo.image = uploaded
                photo.save()
                gallery_added += 1
                self.stdout.write(self.style.SUCCESS(f'        → saved (pk={photo.pk})'))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'        → ERROR: {exc}'))
                errors += 1

        # ── Summary
        self.stdout.write(self.style.MIGRATE_HEADING(f'\n{"─"*60}'))
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'  DRY RUN complete — no changes written.\n'
                f'  Would create: {len(hero_candidates)} hero + {len(gallery_data)} gallery images\n'
                f'  Would skip  : {skipped} duplicate(s)'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ Hero images added  : {hero_added}\n'
                f'  ✓ Gallery photos added: {gallery_added}\n'
                f'  ⟳ Skipped (existing) : {skipped}\n'
                + (f'  ✗ Errors             : {errors}' if errors else '')
            ))
        self.stdout.write(self.style.MIGRATE_HEADING('─'*60 + '\n'))
