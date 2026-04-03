from datetime import timedelta

from django import forms
from django.utils import timezone
from .models import Maintenance
from devis.models import Client

class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        # On ne garde que les champs essentiels
        fields = [
            'client', 'titre', 'type_maintenance',
            'date_maintenance', 'duree_estimee', 'lieu',
            'actions_a_realiser', 
        ]
        widgets = {
            # Type 'date' pour supprimer l'heure
            'date_maintenance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Placeholder modifié pour n'afficher que HH
            'duree_estimee': forms.TextInput(attrs={'type': 'text', 'placeholder': 'Ex: 2', 'class': 'form-control'}),
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
        if self.instance and self.instance.pk:
            duration = self.instance.duree_estimee
            if duration:
                # Si c'est un DurationField (timedelta)
                if isinstance(duration, timedelta):
                    hours = int(duration.total_seconds() // 3600)
                    self.initial['duree_estimee'] = hours
                # Si c'est déjà une chaîne comme '00:00:05'
                elif isinstance(duration, str) and ':' in duration:
                    hours = int(duration.split(':')[0])
                    self.initial['duree_estimee'] = hours

        self.fields['client'].queryset = Client.objects.all().order_by('nom')

class MaintenanceSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Rechercher...', 'class': 'form-control'}))
    statut = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(Maintenance.STATUTS), widget=forms.Select(attrs={'class': 'form-control'}))
    type_maintenance = forms.ChoiceField(required=False, choices=[('', 'Tous')] + list(Maintenance.TYPES_MAINTENANCE), widget=forms.Select(attrs={'class': 'form-control'}))
    date_debut = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    date_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))