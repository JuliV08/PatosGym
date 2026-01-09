from django.db import models
from django.utils.translation import gettext_lazy as _


class TeamMember(models.Model):
    """Staff members - owners, trainers, etc. Editable from Django Admin."""
    ROLE_CHOICES = [
        ('dueno', 'Dueño'),
        ('musculacion', 'Profesor de Musculación'),
        ('funcional', 'Profesor de Funcional'),
        ('clases', 'Profesor de Clases Grupales'),
        ('personal', 'Personal Trainer'),
        ('recepcion', 'Recepción'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(_('Nombre'), max_length=100)
    puesto = models.CharField(_('Puesto'), max_length=50, choices=ROLE_CHOICES)
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
    
    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = _('Miembro del Equipo')
        verbose_name_plural = _('Equipo')
    
    def __str__(self):
        return f"{self.nombre} - {self.get_puesto_display()}"


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
