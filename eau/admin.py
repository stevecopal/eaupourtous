
from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin # <--- Import crucial
from .models import (
    Entreprise, Document, Service, Realisation, 
    Avis, Media,  Valeur 
)
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _






@admin.register(Entreprise)
class EntrepriseAdmin(TranslationAdmin): # On change ModelAdmin par TranslationAdmin
    list_display = ['nom', 'email', 'telephone', 'zone_intervention']
    # Note : Le nom des champs dans fieldsets reste le nom de base (ex: 'slogan')
    # Modeltranslation s'occupe de générer les variantes _fr et _en automatiquement
    fieldsets = (
        ('Identification', {
            'fields': ('nom', 'slogan', 'logo', 'site_web')
        }),
        ('Contact & Localisation', {
            'fields': ('email', 'telephone', 'whatsapp', 'adresse', 'zone_intervention')
        }),
        ('Expertise', {
            'fields': ('description', 'annees_experience')
        }),
    )

@admin.register(Document)
class DocumentAdmin(TranslationAdmin):
    list_display = ['titre', 'type', 'date_ajout', 'actif']
    list_filter = ['type', 'actif', 'date_ajout']
    search_fields = ['titre', 'description']

@admin.register(Service)
class ServiceAdmin(TranslationAdmin):
    list_display = ['titre', 'ordre', 'actif']
    list_editable = ['ordre', 'actif']
    search_fields = ['titre']

@admin.register(Realisation)
class RealisationAdmin(TranslationAdmin):
    list_display = ['titre', 'statut', 'date_realisation', 'localisation', 'mise_en_avant']
    list_filter = ['statut', 'mise_en_avant', 'date_realisation']
    search_fields = ['titre', 'description', 'localisation']
    list_editable = ['mise_en_avant']
    readonly_fields = ['apercu_image']
    
    def apercu_image(self, obj):
        if obj.image_principale:
            return format_html('<img src="{}" style="width: 80px; height: auto; border-radius: 5px;" />', obj.image_principale.url)
        return "Aucune image"
    apercu_image.short_description = "Aperçu visuel"

@admin.register(Avis)
class AvisAdmin(TranslationAdmin):
    list_display = ['nom', 'note', 'date', 'publie']
    list_filter = ['note', 'publie']
    search_fields = ['nom', 'message']
    list_editable = ['publie']

@admin.register(Media)
class MediaAdmin(TranslationAdmin):
    list_display = ['apercu_media', 'titre', 'type', 'date_ajout']
    list_filter = ['type', 'date_ajout']
    search_fields = ['titre', 'description']
    
    def apercu_media(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "-"
    apercu_media.short_description = "Image"

@admin.register(Valeur)
class ValeurAdmin(TranslationAdmin):
    list_display = ['titre', 'icone_view', 'ordre']
    list_editable = ['ordre']
    search_fields = ['titre']

    def icone_view(self, obj):
        return format_html('<i class="{}" style="font-size: 1.2rem; color: #0056b3;"></i> <span style="margin-left:10px">{}</span>', obj.icone, obj.icone)
    icone_view.short_description = "Icône"

