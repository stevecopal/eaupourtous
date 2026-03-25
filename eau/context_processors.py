from .models import Entreprise

def site_data(request):
    """Context processor pour les données globales du site"""
    try:
        entreprise = Entreprise.objects.first()
    except:
        entreprise = None
    
    return {
        'entreprise': entreprise,
    }