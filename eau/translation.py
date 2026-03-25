from modeltranslation.translator import register, TranslationOptions
from .models import Entreprise, Document, Service, Realisation, Avis, Media, Valeur

@register(Entreprise)
class EntrepriseTranslationOptions(TranslationOptions):
    fields = ('slogan', 'adresse', 'description', 'zone_intervention')

@register(Document)
class DocumentTranslationOptions(TranslationOptions):
    fields = ('titre', 'description')

@register(Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('titre', 'description')

@register(Realisation)
class RealisationTranslationOptions(TranslationOptions):
    fields = ('titre', 'description', 'localisation')

@register(Avis)
class AvisTranslationOptions(TranslationOptions):
    fields = ('message',)  # On ne traduit généralement pas le nom de la personne

@register(Media)
class MediaTranslationOptions(TranslationOptions):
    fields = ('titre', 'description')

@register(Valeur)
class ValeurTranslationOptions(TranslationOptions):
    fields = ('titre', 'description')