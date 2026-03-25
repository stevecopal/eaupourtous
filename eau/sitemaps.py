from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Realisation

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'
    
    def items(self):
        return ['home', 'realisations']
    
    def location(self, item):
        return reverse(item)

class RealisationSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6
    
    def items(self):
        return Realisation.objects.filter(statut='termine')
    
    def lastmod(self, obj):
        return obj.date_realisation