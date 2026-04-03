from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Maintenance

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'titre', 'client', 'date_maintenance', 'type_maintenance', 'statut', 'get_notifications_status']
    list_filter = ['type_maintenance', 'statut', 'date_maintenance']
    search_fields = ['reference', 'titre', 'client__nom', 'lieu', ]
    readonly_fields = ['reference', 'date_creation', 'date_notification', 'date_rappel']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('reference', 'client', 'titre', 'description', 'type_maintenance', 'statut')
        }),
        ('Planification', {
            'fields': ('date_maintenance', 'duree_estimee')
        }),
        ('Localisation et équipement', {
            'fields': ('lieu',)
        }),
        ('Travaux à réaliser', {
            'fields': ('actions_a_realiser',)
        }),
        
        ('Notifications', {
            'fields': ('notification_envoyee_client', 'notification_envoyee_admin', 
                      'rappel_envoye', 'date_notification', 'date_rappel'),
            'classes': ('collapse',)
        }),
    )
    
    def get_notifications_status(self, obj):
        if obj.notification_envoyee_client and obj.rappel_envoye:
            return format_html('<span style="color: green;">✓ Notifications OK</span>')
        elif obj.notification_envoyee_client:
            return format_html('<span style="color: orange;">⚠️ Rappel non envoyé</span>')
        else:
            return format_html('<span style="color: red;">✗ Non envoyé</span>')
    
    get_notifications_status.short_description = 'Statut notifications'
    
    actions = ['envoyer_notifications', 'envoyer_rappel']
    
    def envoyer_notifications(self, request, queryset):
        for maintenance in queryset:
            try:
                maintenance.envoyer_notifications_creation()
            except:
                pass
        self.message_user(request, f"Notifications envoyées pour {queryset.count()} maintenance(s)")
    envoyer_notifications.short_description = "Envoyer les notifications"
    
    def envoyer_rappel(self, request, queryset):
        for maintenance in queryset:
            try:
                maintenance.envoyer_rappel()
            except:
                pass
        self.message_user(request, f"Rappels envoyés pour {queryset.count()} maintenance(s)")
    envoyer_rappel.short_description = "Envoyer un rappel"