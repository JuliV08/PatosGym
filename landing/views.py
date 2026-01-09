from django.shortcuts import render
from gallery.models import GalleryPhoto
from .models import TeamMember, HeroImage


def home_view(request):
    """Home page view with gallery, team, and hero carousel integration"""
    # Get featured/recent photos for the landing
    featured_photos = GalleryPhoto.objects.filter(is_active=True)[:12]
    
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
