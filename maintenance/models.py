from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from devis.models import Client  # Import du modèle Client depuis l'app devis
import uuid
from django.db import transaction

class Maintenance(models.Model):
    STATUTS = [
        ('planifiee', _('Planifiée')),
        ('en_cours', _('En cours')),
        ('terminee', _('Terminée')),
        ('annulee', _('Annulée')),
    ]
    
    TYPES_MAINTENANCE = [
        ('preventive', _('Maintenance préventive')),
        ('corrective', _('Maintenance corrective')),
        ('urgente', _('Maintenance urgente')),
    ]
    
    # Identifiant unique
    reference = models.CharField(_("Référence"), max_length=50, unique=True, editable=False)
    
    # Client (lié à l'app devis)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='maintenances')
    
    # Informations générales
    titre = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description détaillée"))
    type_maintenance = models.CharField(_("Type"), max_length=20, choices=TYPES_MAINTENANCE, default='preventive')
    statut = models.CharField(_("Statut"), max_length=20, choices=STATUTS, default='planifiee')
    
    # Dates
    date_creation = models.DateTimeField(_("Date de création"), auto_now_add=True)
    date_maintenance = models.DateTimeField(_("Date de la maintenance"))
    duree_estimee = models.DurationField(_("Durée estimée"), null=True, blank=True, help_text="Durée estimée (HH:MM:SS)")
    
    # Localisation
    lieu = models.CharField(_("Lieu d'intervention"), max_length=255)
    
    # Informations techniques
    actions_a_realiser = models.TextField(_("Actions à réaliser"))
   
    # Notifications
    notification_envoyee_client = models.BooleanField(_("Notification client envoyée"), default=False)
    notification_envoyee_admin = models.BooleanField(_("Notification admin envoyée"), default=False)
    rappel_envoye = models.BooleanField(_("Rappel envoyé"), default=False)
    date_notification = models.DateTimeField(_("Date notification"), null=True, blank=True)
    date_rappel = models.DateTimeField(_("Date rappel"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Maintenance")
        verbose_name_plural = _("Maintenances")
        ordering = ['-date_maintenance']
        indexes = [
            models.Index(fields=['date_maintenance', 'statut']),
            models.Index(fields=['client']),
        ]
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if not self.reference:
            annee = timezone.now().year
            # On cherche la dernière maintenance créée cette année
            derniere_maintenance = Maintenance.objects.filter(
                date_creation__year=annee
            ).order_by('-id').first()

            if derniere_maintenance and derniere_maintenance.reference:
                try:
                    # On extrait le numéro de la référence (ex: '0010' de 'MT-2026-0010')
                    dernier_numero = int(derniere_maintenance.reference.split('-')[-1])
                    nouveau_numero = dernier_numero + 1
                except (ValueError, IndexError):
                    nouveau_numero = 1
            else:
                # Si c'est la toute première de l'année
                nouveau_numero = 1
                
            self.reference = f"MT-{annee}-{nouveau_numero:04d}"
            
        super().save(*args, **kwargs)
        
        if is_new:
            from .tasks import task_envoyer_notifications_creation
            transaction.on_commit(lambda: task_envoyer_notifications_creation.delay(self.id))
            
        def __str__(self):
            return f"{self.reference} - {self.titre} - {self.client.nom}"
    
    @property
    def est_urgente(self):
        return self.type_maintenance == 'urgente'
    
    @property
    def est_en_retard(self):
        return self.date_maintenance < timezone.now() and self.statut not in ['terminee', 'annulee']
    
    def envoyer_notifications_creation(self):
        """Envoyer les notifications à la création"""
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        # Notification au client
        sujet_client = f"[MAINTENANCE] {self.reference} - {self.titre}"
        contexte_client = {
            'maintenance': self,
            'client': self.client,
            'type': 'creation'
        }
        html_client = render_to_string('emails/notification_client.html', contexte_client)
        texte_client = strip_tags(html_client)
        if self.client.email:
            send_mail(
                sujet_client,
                texte_client,
                settings.DEFAULT_FROM_EMAIL,
                [self.client.email],
                html_message=html_client,
                fail_silently=False,
            )
        
        # Notification à l'admin
        sujet_admin = f"[MAINTENANCE] Nouvelle maintenance créée - {self.reference}"
        contexte_admin = {
            'maintenance': self,
            'client': self.client,
            'type': 'creation'
        }
        html_admin = render_to_string('emails/notification_admin.html', contexte_admin)
        texte_admin = strip_tags(html_admin)
        
        send_mail(
            sujet_admin,
            texte_admin,
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            html_message=html_admin,
            fail_silently=False,
        )
        
        self.notification_envoyee_client = True
        self.notification_envoyee_admin = True
        self.date_notification = timezone.now()
        self.save(update_fields=['notification_envoyee_client', 'notification_envoyee_admin', 'date_notification'])    
    def envoyer_rappel(self):
        """Envoyer un rappel un jour avant avec gestion des deux templates"""
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        from django.contrib.sites.models import Site # Optionnel, pour le domaine

        # 1. On prépare le contexte complet pour satisfaire les deux templates
        contexte = {
            'maintenance': self,
            'client': self.client,
            'type': 'rappel',
            'protocol': 'https', # ou 'http' en local
            'domain': 'eaupourtous.cm', # Ton domaine
            'entreprise': {
                'nom': 'Eau Pour Tous',
                'telephone': '+237 6XX XX XX XX',
                'email': 'contact@eaupourtous.cm'
            }
        }

        # 2. Rappel au CLIENT (Template orange/blanc détaillé)
        if self.client.email:
            sujet_client = f"⏰ Rappel : Votre intervention demain ({self.reference})"
            html_client = render_to_string('emails/rappel_client.html', contexte)
            texte_client = strip_tags(html_client)
            
            send_mail(
                sujet_client,
                texte_client,
                settings.DEFAULT_FROM_EMAIL,
                [self.client.email],
                html_message=html_client,
                fail_silently=False,
            )

        # 3. Rappel à l'ADMIN / ÉQUIPE (Template avec bandeau jaune ⚠️)
        sujet_admin = f"⚠️ RAPPEL INTERNE : Maintenance demain - {self.reference}"
        # Utilise bien le nom de ton second fichier HTML ici
        html_admin = render_to_string('emails/rappel_admin.html', contexte)
        texte_admin = strip_tags(html_admin)
        
        admin_dest = getattr(settings, 'ADMIN_EMAIL', settings.EMAIL_HOST_USER)
        
        send_mail(
            sujet_admin,
            texte_admin,
            settings.DEFAULT_FROM_EMAIL,
            [admin_dest],
            html_message=html_admin,
            fail_silently=False,
        )

        # 4. Enregistrement de l'état
        self.rappel_envoye = True
        self.date_rappel = timezone.now()
        self.save(update_fields=['rappel_envoye', 'date_rappel'])