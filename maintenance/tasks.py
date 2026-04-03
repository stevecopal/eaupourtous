from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Maintenance
@shared_task
def task_envoyer_notifications_creation(maintenance_id):
    """Tâche asynchrone pour les notifications immédiates"""
    try:
        maintenance = Maintenance.objects.get(id=maintenance_id)
        maintenance.envoyer_notifications_creation()
    except Maintenance.DoesNotExist:
        pass

@shared_task
def task_verifier_et_envoyer_rappels():
    """Vérifie les interventions prévues dans environ 24h à 48h"""
    maintenant = timezone.now()
    # On définit une fenêtre : entre maintenant et demain à la même heure
    demain = maintenant + timedelta(days=1)
    
    # On filtre : 
    # 1. Statut planifié uniquement
    # 2. Date comprise entre maintenant et demain
    # 3. Rappel pas encore envoyé
    maintenances = Maintenance.objects.filter(
        statut='planifiee',
        date_maintenance__gt=maintenant, # Pas les interventions passées
        date_maintenance__lte=demain,    # Celles qui arrivent dans les 24h
        rappel_envoye=False
    )
    
    for m in maintenances:
        m.envoyer_rappel()