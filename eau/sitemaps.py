from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Realisation

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        # On ne met que les pages fixes ici
        return ['home', 'realisations', 'contact'] 

    def location(self, item):
        return reverse(item)

class RealisationSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Realisation.objects.all()

    def location(self, item):
        # On pointe vers la nouvelle URL de détail avec l'ID (pk)
        return reverse('realisation_detail', kwargs={'pk': item.pk})