import os

from django import forms
from django.forms import inlineformset_factory
from .models import Devis, SectionDevis, LigneDevis
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import Rapport

class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = ['client', 'objet', 'date_validite', 'statut']
        widgets = {
            'date_validite': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none'}),
            'objet': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none', 'placeholder': _("Ex: Forage à Pouma")}),
            'client': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none'}),
            'statut': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none'}),
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = SectionDevis
        fields = ['titre', 'ordre']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full font-bold border-b-2 border-red-500 focus:outline-none mb-2', 'placeholder': _("Titre de la Section (ex: FORAGE)")}),
            'ordre': forms.HiddenInput(),
        }

# Formset pour les lignes d'une section
LigneFormSet = inlineformset_factory(
    SectionDevis, LigneDevis,
    fields=['designation', 'unite', 'prix_unitaire', 'quantite'],
    extra=1,
    can_delete=True,
    widgets={
        'designation': forms.TextInput(attrs={'class': 'w-full p-2 border rounded', 'placeholder': _('Désignation')}),
        'unite': forms.TextInput(attrs={'class': 'w-full p-2 border rounded text-center', 'placeholder': 'ff'}),
        'prix_unitaire': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded text-right pu-field', 'onchange': 'updateRowTotal(this)'}),
        'quantite': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded text-center qte-field', 'onchange': 'updateRowTotal(this)'}),
    }
)




from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'email', 'telephone', 'adresse']

        email = forms.EmailField(
            required=False, 
            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@email.com (Optionnel)'})
        )
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse physique'}),
        }




class RapportForm(forms.ModelForm):
    class Meta:
        model = Rapport
        fields = ['client', 'nom', 'fichier']
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-control w-full pl-10 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 h-11',
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control w-full pl-10 rounded-xl border-slate-200 focus:border-blue-500 focus:ring-blue-500 h-11',
                'placeholder': 'Ex: Rapport d\'analyse forage PK12'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-1',
            }),
        }

    def clean_fichier(self):
        file = self.cleaned_data.get('fichier')
        if file:
            extension = os.path.splitext(file.name)[1].lower()
            if extension not in ['.pdf', '.doc', '.docx']:
                raise forms.ValidationError("Seuls les fichiers PDF et Word sont autorisés.")
        return file