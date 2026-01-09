from django.shortcuts import render
from .models import GalleryPhoto


def gallery_view(request):
    """Public gallery view showing only active photos"""
    photos = GalleryPhoto.objects.filter(is_active=True).select_related()
    
    context = {
        'photos': photos,
        'categories': dict(GalleryPhoto.CATEGORY_CHOICES),
    }
    
    return render(request, 'gallery/gallery.html', context)
