from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose
import os


def validate_image_size(image):
    """Validate image file size (max 20MB)"""
    filesize = image.size
    if filesize > 20 * 1024 * 1024:  # 20MB
        raise ValidationError("El tamaño máximo del archivo es 20MB")


def sanitize_filename(filename):
    """Sanitize filename, removing special characters"""
    name, ext = os.path.splitext(filename)
    # Remove special characters, keep only alphanumeric and hyphens
    name = "".join(c if c.isalnum() or c in '-_' else '_' for c in name)
    return f"{name}{ext}".lower()


def gallery_upload_path(instance, filename):
    """Generate upload path for gallery images"""
    sanitized = sanitize_filename(filename)
    return f'gallery/{sanitized}'


class GalleryPhoto(models.Model):
    """Model for gallery photos with automatic thumbnail generation"""
    
    CATEGORY_CHOICES = [
        ('vestuarios', 'Vestuarios'),
        ('cardio', 'Cardio'),
        ('elgym', 'El Gym'),
        ('musculacion', 'Musculación'),
        ('transformaciones', 'Antes y Después'),
        ('atletas', 'Nuestros Atletas'),
    ]
    
    image = models.ImageField(
        upload_to=gallery_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size,
        ],
        verbose_name='Imagen'
    )
    
    thumbnail = ImageSpecField(
        source='image',
        processors=[Transpose(), ResizeToFill(400, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    caption = models.TextField(
        blank=True,
        verbose_name='Descripción/Caption'
    )
    
    alt_text = models.CharField(
        max_length=200,
        verbose_name='Texto alternativo (ALT)',
        help_text='Descripción de la imagen para accesibilidad y SEO'
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Visible'
    )
    
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Número menor aparece primero'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    
    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'Foto de Galería'
        verbose_name_plural = 'Fotos de Galería'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    def save(self, *args, **kwargs):
        # Sanitize filename before saving
        if self.image:
            self.image.name = sanitize_filename(self.image.name)
        super().save(*args, **kwargs)
