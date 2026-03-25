from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('realisations/', views.RealisationListView.as_view(), name='realisations'),
    path('api/realisations/', views.realisations_api, name='realisations_api'),
    path('contact/', views.ContactView.as_view(), name='contact'),

]