from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from eau.sitemaps import StaticViewSitemap, RealisationSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'realisations': RealisationSitemap,
}

# 1. URLs SANS préfixe de langue (Obligatoire pour set_language)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), # <--- INDISPENSABLE ICI
]

# 2. URLs AVEC préfixe de langue (/fr/, /en/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('eau.urls')),
    path('devis/', include('devis.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    prefix_default_language=True # Optionnel : ajoute /fr/ même pour la langue par défaut
)

# 3. Gestion des fichiers médias et statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)