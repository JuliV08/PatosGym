from django.contrib import admin
from django.utils.html import format_html
from .models import TeamMember, HeroImage


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puesto', 'foto_preview', 'orden', 'activo')
    list_editable = ('orden', 'activo')
    list_filter = ('puesto', 'activo')
    search_fields = ('nombre',)
    ordering = ('orden', 'nombre')
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 50%;" />', obj.foto.url)
        return "-"
    foto_preview.short_description = "Foto"


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'imagen_preview', 'orden', 'activo')
    list_editable = ('orden', 'activo')
    list_filter = ('activo',)
    ordering = ('orden',)
    
    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="height: 50px; width: 90px; object-fit: cover; border-radius: 4px;" />', obj.imagen.url)
        return "-"
    imagen_preview.short_description = "Preview"
