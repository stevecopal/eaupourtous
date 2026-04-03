from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib import messages
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django.core.mail import send_mail
from django.shortcuts import redirect

from eau.forms import ContactForm, LoginForm
from eau.tasks import send_contact_email_task
from django.shortcuts import render
from devis.models import Devis, Client
from django.db.models import Sum

from maintenance.models import Maintenance
from .models import (
    Entreprise, Service, Realisation, Avis, 
    Valeur, Media, Document
)

class IndexView(TemplateView):
    """Vue principale de la landing page"""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupération des données dynamiques
        context['services'] = Service.objects.filter(actif=True)
        context['valeurs'] = Valeur.objects.all()
        context['realisations'] = Realisation.objects.all()[:6]
        context['avis'] = Avis.objects.filter(publie=True)[:6]
        context['documents'] = Document.objects.filter(actif=True)[:3]
        context['medias'] = Media.objects.all
        context['contact_form'] = ContactForm()
        
        return context

class RealisationListView(ListView):
    """Vue pour la liste des réalisations"""
    model = Realisation
    template_name = 'realisations/list.html'
    context_object_name = 'realisations'
    paginate_by = 9
    
    def get_queryset(self):
        return Realisation.objects.all().order_by('-date_realisation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'total': Realisation.objects.count(),
            'termines': Realisation.objects.filter(statut='termine').count(),
            'en_cours': Realisation.objects.filter(statut='en_cours').count(),
        }
        return context

def realisations_api(request):
    """API simple pour le chargement AJAX des réalisations"""
    page = request.GET.get('page', 1)
    realisations = Realisation.objects.filter(statut='termine').order_by('-date_realisation')
    paginator = Paginator(realisations, 6)
    
    try:
        realisations_page = paginator.page(page)
    except:
        return JsonResponse({'error': 'Page invalide'}, status=400)
    
    data = []
    for r in realisations_page:
        data.append({
            'id': r.id,
            'titre': r.titre,
            'description': r.description[:100],
            'image': r.image_principale.url if r.image_principale else '',
            'localisation': r.localisation,
            'date': r.date_realisation.strftime('%d/%m/%Y'),
        })
    
    return JsonResponse({
        'realisations': data,
        'has_next': realisations_page.has_next(),
        'has_previous': realisations_page.has_previous(),
        'current_page': realisations_page.number,
    })

def page_not_found(request, exception):
    """Page 404 personnalisée"""
    return render(request, '404.html', status=404)

def server_error(request):
    """Page 500 personnalisée"""
    return render(request, '500.html', status=500)



from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class ContactView(FormView):
    form_class = ContactForm
    template_name = 'index.html'

    def get_success_url(self):
        return reverse('home') + '#contact'

    def form_valid(self, form):
        # On récupère les données propres
        data = form.cleaned_data
        
        # On lance la tâche en arrière-plan (delay)
        # On passe les données simples (dict) car Celery doit les sérialiser
        send_contact_email_task.delay(data)
        
        # Réponse instantanée pour l'utilisateur
        messages.success(self.request, _("Votre demande est en cours de traitement. Un accusé de réception vous sera envoyé."))
        
        return super().form_valid(form)



from django.views.generic import DetailView
from .models import Realisation

class RealisationDetailView(DetailView):
    model = Realisation
    template_name = 'realisations/realisation_detail.html'  # Le nom de ton fichier HTML
    context_object_name = 'realisation'           # Le nom de la variable dans ton HTML


from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from devis.models import Client, Devis

class CustomLoginView(LoginView):
    template_name = 'eau/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

def dashboard(request):
    context = {
        'total_devis': Devis.objects.count(),
        'total_clients': Client.objects.count(),
        'maintenances_count': Maintenance.objects.count(),
        'derniers_devis': Devis.objects.order_by('-date_creation')[:5],
        'ca_total': Devis.objects.aggregate(Sum('total_ht'))['total_ht__sum'] or 0,
    }
    return render(request, 'eau/dashboard.html', context)
    
class CustomLogoutView(LogoutView):
    next_page = 'home' # Redirige vers login après déconnexion