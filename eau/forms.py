from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm

class ContactForm(forms.Form):
    """Formulaire de contact minimaliste sans labels externes"""
    
    nom = forms.CharField(
        label='', # On vide le label
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none transition-all',
            'placeholder': _('Nom complet')
        })
    )
    
    email = forms.EmailField(
        label='', 
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none transition-all',
            'placeholder': _('Adresse Email')
        })
    )
    
    telephone = forms.CharField(
        label='',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none transition-all',
            'placeholder': _('Téléphone')
        })
    )
    
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-5 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-brand-blue focus:border-transparent outline-none transition-all',
            'rows': 4,
            'placeholder': _('Comment pouvons-nous vous aider ? Décrivez votre projet...')
        })
    )




from django.utils.translation import gettext_lazy as _

class LoginForm(AuthenticationForm):
    """Formulaire de connexion stylisé avec Tailwind"""
    
    username = forms.CharField(
        label=_("Nom d'utilisateur"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
            'placeholder': _("Ex: admin_copal"),
        })
    )
    
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-slate-200 focus:ring-2 focus:ring-blue-500 outline-none transition',
            'placeholder': '••••••••',
        })
    )