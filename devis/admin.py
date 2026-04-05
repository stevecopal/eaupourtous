from django.contrib import admin
from .models import Client, Devis, SectionDevis, LigneDevis
from django.utils.html import format_html
from .models import Rapport
from django.utils.translation import gettext_lazy as _

class LigneInline(admin.TabularInline):
    model = LigneDevis
    extra = 1

@admin.register(SectionDevis)
class SectionAdmin(admin.ModelAdmin):
    inlines = [LigneInline]
    list_filter = ['devis']

class SectionInline(admin.StackedInline):
    model = SectionDevis
    extra = 1

@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'total_ht', 'statut')
    inlines = [SectionInline]





@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'date_creation')
    search_fields = ('nom', 'email')
    
    # def get_activity(self, obj):
    #     return _("%(devis)s Devis / %(maint)s Maint.") % {
    #         'devis': obj.total_devis,
    #         # 'maint': obj.total_maintenances
    #     }
    # get_activity.short_description = _("Activité")

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('nom', 'client', 'date_creation', 'actions_link')
    list_filter = ('client', 'date_creation')
    search_fields = ('nom', 'client__nom')

    def actions_link(self, obj):
        # On crée des boutons pour Voir et Télécharger
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color: #264b5d; color: white; padding: 3px 10px; margin-right: 5px; border-radius: 4px;">👁️ Voir</a>'
            '<a class="button" href="{}" download style="background-color: #f59e0b; color: white; padding: 3px 10px; border-radius: 4px;">📥 Télécharger</a>',
            obj.fichier.url,
            obj.fichier.url
        )
    
    actions_link.short_description = _("Actions")

