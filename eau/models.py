
# Create your models here.


from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.contrib.auth.models import AbstractUser






class Entreprise(models.Model):
    """Modèle pour les informations de l'entreprise"""
    nom = models.CharField(_('Nom'), max_length=200, default='Eau pour tous SARL')
    slogan = models.CharField(_('Slogan'), max_length=500, blank=True)
    logo = models.ImageField(_('Logo'), upload_to='media/', blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=200)
    telephone = models.CharField(_('Téléphone'), max_length=50)
    whatsapp = models.CharField(_('WhatsApp'), max_length=50, blank=True)
    adresse = models.TextField(_('Adresse'), default='Douala, Cameroun')
    description = models.TextField(_('Description'))
    zone_intervention = models.CharField(_("Zone d'intervention"), max_length=200, default='Tout le Cameroun')
    site_web = models.URLField(_('Site web'), blank=True)
    annees_experience = models.IntegerField(_("Années d'expérience"), default=10)
    
    class Meta:
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")
    
    def __str__(self):
        return self.nom

class Document(models.Model):
    """Modèle pour les documents officiels"""
    TYPES = [
        ('fiscal', 'Fiscal'),
        ('legal', 'Légal'),
        ('administratif', 'Administratif'),
        ('certification', 'Certification'),
    ]
    
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    fichier = models.ImageField(_('Fichier'), upload_to='media/')
    type = models.CharField(_('Type'), max_length=50, choices=TYPES)
    date_ajout = models.DateTimeField(_("Date d'ajout"), auto_now_add=True)
    actif = models.BooleanField(_('Actif'), default=True)
    
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ['-date_ajout']
    
    def __str__(self):
        return self.titre

class Service(models.Model):
    """Modèle pour les services"""
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    icone = models.CharField(_('Icône (FontAwesome)'), max_length=100, default='fas fa-tools')
    ordre = models.IntegerField(_('Ordre'), default=0)
    actif = models.BooleanField(_('Actif'), default=True)
    
    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ['ordre', 'titre']
    
    def __str__(self):
        return self.titre

class Realisation(models.Model):
    """Modèle pour les réalisations"""
    STATUTS = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]
    
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    image_principale = models.ImageField(_('Image principale'), upload_to='media/')
    galerie = models.JSONField(_('Galerie'), blank=True, null=True, help_text="Liste des URLs d'images")
    statut = models.CharField(_('Statut'), max_length=20, choices=STATUTS, default='termine')
    date_realisation = models.DateField(_('Date de réalisation'))
    localisation = models.CharField(_('Localisation'), max_length=200, blank=True)
    mise_en_avant = models.BooleanField(_('Mise en avant'), default=False)
    
    class Meta:
        verbose_name = _("Réalisation")
        verbose_name_plural = _("Réalisations")
        ordering = ['-date_realisation']
    
    def __str__(self):
        return self.titre
    
    def get_absolute_url(self):
        # Remplace 'realisation_detail' par le 'name' de ton URL de détail
        return reverse('realisations')

class Avis(models.Model):
    """Modèle pour les avis clients"""
    nom = models.CharField(_('Nom'), max_length=200)
    message = models.TextField(_('Message'))
    note = models.IntegerField(_('Note'), choices=[(i, i) for i in range(1, 6)])
    date = models.DateTimeField(_('Date'), auto_now_add=True)
    publie = models.BooleanField(_('Publié'), default=True)
    
    class Meta:
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis")
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.nom} - {self.note}/5"

class Media(models.Model):
    """Modèle pour la galerie média"""
    TYPES = [
        ('equipe', 'Équipe'),
        ('chantier', 'Chantier'),
        ('materiel', 'Matériel'),
        ('autre', 'Autre'),
    ]
    
    image = models.ImageField(_('Image'), upload_to='media/')
    titre = models.CharField(_('Titre'), max_length=200, blank=True)
    description = models.TextField(_('Description'), blank=True)
    type = models.CharField(_('Type'), max_length=50, choices=TYPES)
    date_ajout = models.DateTimeField(_("Date d'ajout"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Média")
        verbose_name_plural = _("Médias")
        ordering = ['-date_ajout']
    
    def __str__(self):
        return self.titre or f"Media {self.id}"

class Valeur(models.Model):
    """Modèle pour les valeurs de l'entreprise (Pourquoi nous choisir)"""
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    icone = models.CharField(_('Icône (FontAwesome)'), max_length=100)
    ordre = models.IntegerField(_('Ordre'), default=0)
    
    class Meta:
        verbose_name = _("Valeur")
        verbose_name_plural = _("Valeurs")
        ordering = ['ordre']
    
    def __str__(self):
        return self.titre
    

# authentification
