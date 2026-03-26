from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3) # Gère jusqu'à 3 tentatives en cas d'échec
def send_contact_email_task(self, data):
    try:
        sujet = f"🚀 Nouveau Projet : {data['nom']}"
        
        # Le rendu se fait maintenant dans le worker Celery
        html_message = render_to_string('emails/contact_email.html', data)
        plain_message = strip_tags(html_message)
        
        send_mail(
            sujet,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Email envoyé avec succès de {data['email']}"
        
    except Exception as exc:
        # En cas d'erreur (ex: Gmail down), Celery réessaie après 5 minutes
        logger.error(f"Erreur envoi mail: {exc}")
        raise self.retry(exc=exc, countdown=300)