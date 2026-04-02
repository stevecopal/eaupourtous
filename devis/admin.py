from django.contrib import admin
from .models import Client, Devis, SectionDevis, LigneDevis

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