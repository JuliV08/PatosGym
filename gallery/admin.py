from django.contrib import admin
from django.utils.html import format_html
from .models import GalleryPhoto


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_preview', 'title', 'category', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'caption', 'alt_text']
    list_editable = ['is_active', 'sort_order']
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Imagen', {
            'fields': ('image', 'image_preview')
        }),
        ('Información', {
            'fields': ('title', 'caption', 'alt_text', 'category')
        }),
        ('Configuración', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        """Show thumbnail in list view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail.url if obj.thumbnail else obj.image.url
            )
        return '-'
    thumbnail_preview.short_description = 'Vista previa'
    
    def image_preview(self, obj):
        """Show full image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 400px; border-radius: 8px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Preview de la imagen'
    
    class Media:
        css = {
            'all': ('admin/css/gallery_admin.css',)
        }
