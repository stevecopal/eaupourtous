from django import forms
from django.utils import timezone
from .models import Maintenance
from devis.models import Client

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'client', 'titre', 'description', 'type_maintenance',
            'date_maintenance', 'duree_estimee', 'lieu',
            'actions_a_realiser', 
        ]
        widgets = {
            'date_maintenance': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'duree_estimee': forms.TextInput(attrs={'type': 'text', 'placeholder': 'HH:MM:SS', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'actions_a_realiser': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'type_maintenance': forms.Select(attrs={'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.all().order_by('nom')
        self.fields['date_maintenance'].required = True
        self.fields['lieu'].required = True
        self.fields['actions_a_realiser'].required = True

class MaintenanceSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Rechercher...', 'class': 'form-control'}))
    statut = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(Maintenance.STATUTS), widget=forms.Select(attrs={'class': 'form-control'}))
    type_maintenance = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(Maintenance.TYPES_MAINTENANCE), widget=forms.Select(attrs={'class': 'form-control'}))
    date_debut = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))