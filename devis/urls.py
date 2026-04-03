from django.urls import path
from . import views

urlpatterns = [
    path('', views.devis_list, name='devis_list'),
    path('nouveau/', views.devis_create, name='devis_create'),
    path('modifier/<int:pk>/', views.devis_update, name='devis_edit'),
    path('details/<int:pk>/', views.devis_detail, name='devis_detail'),
    path('supprimer/<int:pk>/', views.devis_delete, name='devis_delete'),
    path('imprimer/<int:pk>/', views.generate_pdf, name='generate_pdf'),
    path('statut/<int:pk>/<str:status>/', views.update_devis_status, name='update_status'),



    path('clients/', views.client_list, name='client_list'),
    # path('clients/recherche/', views.client_search, name='client_search'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/creer/', views.client_create, name='client_create'),
    path('clients/<int:pk>/modifier/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),
]