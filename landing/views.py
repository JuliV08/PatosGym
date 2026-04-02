from itertools import chain
from django.shortcuts import render
from gallery.models import GalleryPhoto
from .models import TeamMember, HeroImage

PREVIEW_PER_CATEGORY = 3


def home_view(request):
    """Home page view with gallery, team, and hero carousel integration"""
    # Load up to PREVIEW_PER_CATEGORY photos per category so every filter tab
    # has photos and the preview stays small regardless of total photo count.
    categories = [c for c, _ in GalleryPhoto.CATEGORY_CHOICES]
    featured_photos = list(chain.from_iterable(
        GalleryPhoto.objects.filter(is_active=True, category=cat)[:PREVIEW_PER_CATEGORY]
        for cat in categories
    ))
    
    # Get active team members
    team_members = TeamMember.objects.filter(activo=True)
    
    # Get active hero images for carousel
    hero_images = HeroImage.objects.filter(activo=True)
    
    context = {
        'featured_photos': featured_photos,
        'team_members': team_members,
        'hero_images': hero_images,
    }
    
    return render(request, 'landing/home.html', context)
