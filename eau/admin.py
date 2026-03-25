from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Entreprise, Document, Service, Realisation, 
    Avis, Media, Valeur
)

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'telephone', 'zone_intervention']
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'slogan', 'logo', 'site_web')
        }),
        ('Contact', {
            'fields': ('email', 'telephone', 'whatsapp', 'adresse')
        }),
        ('Présentation', {
            'fields': ('description', 'zone_intervention', 'annees_experience')
        }),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type', 'date_ajout', 'actif']
    list_filter = ['type', 'actif']
    search_fields = ['titre', 'description']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['titre', 'ordre', 'actif']
    list_editable = ['ordre', 'actif']
    search_fields = ['titre']

@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'statut', 'date_realisation', 'localisation', 'mise_en_avant']
    list_filter = ['statut', 'mise_en_avant']
    search_fields = ['titre', 'description']
    list_editable = ['mise_en_avant']
    readonly_fields = ['apercu_image']
    
    def apercu_image(self, obj):
        if obj.image_principale:
            return format_html('<img src="{}" width="100" />', obj.image_principale.url)
        return "Aucune image"
    apercu_image.short_description = "Aperçu"

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['nom', 'note', 'date', 'publie']
    list_filter = ['note', 'publie']
    search_fields = ['nom', 'message']
    list_editable = ['publie']

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['titre', 'type', 'date_ajout']
    list_filter = ['type']
    search_fields = ['titre', 'description']

@admin.register(Valeur)
class ValeurAdmin(admin.ModelAdmin):
    list_display = ['titre', 'icone', 'ordre']
    list_editable = ['ordre']
    search_fields = ['titre']