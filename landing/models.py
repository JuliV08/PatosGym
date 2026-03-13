from django.db import models
from django.utils.translation import gettext_lazy as _


class TeamMember(models.Model):
    """Staff members - owners, trainers, etc. Editable from Django Admin."""
    ROLE_CHOICES = [
        ('dueno', 'Dueño'),
        ('duena', 'Dueña'),
        ('profesor_musculacion', 'Profesor de Musculación'),
        ('profesora_musculacion', 'Profesora de Musculación'),
        ('personal_trainer', 'Personal Trainer'),
        ('recepcionista', 'Recepcionista'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(_('Nombre'), max_length=100)
    puesto = models.CharField(_('Puesto Principal'), max_length=50, choices=ROLE_CHOICES)
    puesto_secundario = models.CharField(
        _('Puesto Secundario'),
        max_length=50,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        help_text=_('Puesto adicional (opcional). Ej: Personal Trainer si también es profesor')
    )
    foto = models.ImageField(
        _('Foto'),
        upload_to='staff/',
        blank=True,
        null=True,
        help_text=_('Imagen del miembro del equipo')
    )
    cv_info = models.TextField(
        _('Bio / Experiencia'),
        blank=True,
        help_text=_('Información sobre experiencia y trayectoria')
    )
    orden = models.PositiveIntegerField(_('Orden'), default=0, help_text=_('Número menor aparece primero'))
    activo = models.BooleanField(_('Activo'), default=True)
    video_file = models.FileField(
        _('Video de Entrevista (MP4)'),
        upload_to='staff_videos/',
        blank=True,
        null=True,
        help_text=_('Archivo de video en formato .mp4 (Peso máximo recomendado: 30MB). Reemplaza al link de YouTube.')
    )
    
    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = _('Miembro del Equipo')
        verbose_name_plural = _('Equipo')
    
    def __str__(self):
        return f"{self.nombre} - {self.get_puesto_display()}"
    
    def get_full_role_display(self):
        """Get both primary and secondary roles if exists"""
        if self.puesto_secundario:
            return f"{self.get_puesto_display()} / {self.get_puesto_secundario_display()}"
        return self.get_puesto_display()


class HeroImage(models.Model):
    """Dynamic hero carousel images - managed from Django Admin."""
    imagen = models.ImageField(
        _('Imagen'),
        upload_to='hero/',
        help_text=_('Imagen para el carrusel del hero (recomendado: 1920x1080 o superior)')
    )
    titulo = models.CharField(
        _('Título'),
        max_length=100,
        blank=True,
        help_text=_('Título opcional para SEO/alt text')
    )
    orden = models.PositiveIntegerField(_('Orden'), default=0, help_text=_('Número menor aparece primero'))
    activo = models.BooleanField(_('Activo'), default=True)
    
    class Meta:
        ordering = ['orden']
        verbose_name = _('Imagen Hero')
        verbose_name_plural = _('Imágenes Hero')
    
    def __str__(self):
        return self.titulo or f"Hero #{self.pk}"
