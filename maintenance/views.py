from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Maintenance
from .forms import MaintenanceForm, MaintenanceSearchForm
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

@login_required
def maintenance_list(request):
    """Liste des maintenances"""
    form = MaintenanceSearchForm(request.GET)
    maintenances = Maintenance.objects.all().select_related('client')
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        statut = form.cleaned_data.get('statut')
        type_maint = form.cleaned_data.get('type_maintenance')
        date_debut = form.cleaned_data.get('date_debut')
        date_fin = form.cleaned_data.get('date_fin')
        
        if search:
            maintenances = maintenances.filter(
                Q(reference__icontains=search) |
                Q(titre__icontains=search) |
                Q(client__nom__icontains=search) |
                Q(lieu__icontains=search)
            )
        if statut:
            maintenances = maintenances.filter(statut=statut)
        if type_maint:
            maintenances = maintenances.filter(type_maintenance=type_maint)
        if date_debut:
            maintenances = maintenances.filter(date_maintenance__date__gte=date_debut)
        if date_fin:
            maintenances = maintenances.filter(date_maintenance__date__lte=date_fin)
    queryset = Maintenance.objects.all()      
    total = queryset.count()
    # "À venir" : Statut planifié ET date future
    maintenances_a_venir = queryset.filter(statut='planifiee', date_maintenance__gt=timezone.now()).count()
    # "En retard" : Statut non terminé ET date passée
    en_retard = queryset.filter(statut__in=['planifiee', 'en_cours'], date_maintenance__lt=timezone.now()).count()
    # "Terminées"
    completed_count = queryset.filter(statut='terminee').count()
    paginator = Paginator(maintenances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'total': maintenances.count(),
        'en_retard': maintenances.filter(date_maintenance__lt=timezone.now(), statut__in=['planifiee', 'en_cours']).count(),
        'maintenances': queryset, # Les données pour la table
        'total': total,
        'maintenances_a_venir': maintenances_a_venir, # Utilise cette variable précise
        'en_retard': en_retard,
        'completed_count': completed_count,
    }
    return render(request, 'maintenance/maintenance_list.html', context)

@login_required
def maintenance_create(request):
    """Créer une nouvelle maintenance"""
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save()
            
            # Envoyer les notifications immédiates
            try:
                maintenance.envoyer_notifications_creation()
                messages.success(request, f'Maintenance {maintenance.reference} créée avec succès. Les notifications ont été envoyées.')
            except Exception as e:
                messages.warning(request, f'Maintenance créée mais erreur lors de l\'envoi des notifications: {str(e)}')
            
            # Programmer le rappel pour la veille
            try:
                from .tasks import schedule_rappel_maintenance
                schedule_rappel_maintenance(maintenance.id)
            except:
                pass
            
            return redirect('maintenance_detail', pk=maintenance.pk)
    else:
        form = MaintenanceForm()
    
    context = {'form': form, 'title': 'Nouvelle maintenance'}
    return render(request, 'maintenance/maintenance_form.html', context)

@login_required
def maintenance_update(request, pk):
    """Modifier une maintenance"""
    maintenance = get_object_or_404(Maintenance, pk=pk)
    
    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance)
        if form.is_valid():
            maintenance = form.save()
            messages.success(request, f'Maintenance {maintenance.reference} modifiée avec succès.')
            return redirect('maintenance_detail', pk=maintenance.pk)
    else:
        form = MaintenanceForm(instance=maintenance)
    
    context = {'form': form, 'title': 'Modifier maintenance', 'maintenance': maintenance}
    return render(request, 'maintenance/maintenance_form.html', context)

@login_required
def maintenance_detail(request, pk):
    """Détail d'une maintenance"""
    maintenance = get_object_or_404(Maintenance, pk=pk)
    context = {'maintenance': maintenance}
    return render(request, 'maintenance/maintenance_detail.html', context)

@login_required
@require_http_methods(["POST"])
def maintenance_delete(request, pk):
    """Supprimer une maintenance"""
    maintenance = get_object_or_404(Maintenance, pk=pk)
    reference = maintenance.reference
    maintenance.delete()
    messages.success(request, f'Maintenance {reference} supprimée avec succès.')
    return redirect('maintenance_list')

@login_required
@require_http_methods(["POST"])
def maintenance_change_status(request, pk):
    """Changer le statut d'une maintenance"""
    maintenance = get_object_or_404(Maintenance, pk=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Maintenance.STATUTS):
        maintenance.statut = new_status
        maintenance.save()
        messages.success(request, f'Statut de la maintenance {maintenance.reference} mis à jour.')
    
    return redirect('maintenance_detail', pk=maintenance.pk)

@login_required
def maintenance_calendar(request):
    """Vue calendrier des maintenances"""
    maintenances = Maintenance.objects.filter(
        statut__in=['planifiee', 'en_cours']
    ).select_related('client')
    
    events = []
    for maint in maintenances:
        events.append({
            'id': maint.id,
            'title': f"{maint.titre} - {maint.reference}",
            'start': maint.date_maintenance.isoformat(),
            'end': (maint.date_maintenance + maint.duree_estimee).isoformat() if maint.duree_estimee else maint.date_maintenance.isoformat(),
            'url': f"/maintenance/{maint.id}/",
            'backgroundColor': '#dc3545' if maint.type_maintenance == 'urgente' else '#007bff',
            'borderColor': '#dc3545' if maint.type_maintenance == 'urgente' else '#007bff',
            'textColor': 'white',
            'extendedProps': {
                'client': maint.client.nom,
                'lieu': maint.lieu,
                'type': maint.get_type_maintenance_display(),
                'statut': maint.get_statut_display(),
            }
        })
    
    context = {'events': json.dumps(events)}
    return render(request, 'maintenance/maintenance_calendar.html', context)

@login_required
def maintenance_send_reminder(request, pk):
    """Envoyer manuellement un rappel"""
    maintenance = get_object_or_404(Maintenance, pk=pk)
    
    try:
        maintenance.envoyer_rappel()
        messages.success(request, f'Rappel envoyé pour la maintenance {maintenance.reference}')
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'envoi du rappel: {str(e)}')
    
    return redirect('maintenance_detail', pk=maintenance.pk)