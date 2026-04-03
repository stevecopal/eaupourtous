from django.urls import path
from . import views


urlpatterns = [
    path('', views.maintenance_calendar, name='maintenance_calendar'),
    path('creer/', views.maintenance_create, name='maintenance_create'),
    path('<int:pk>/', views.maintenance_detail, name='maintenance_detail'),
    path('<int:pk>/modifier/', views.maintenance_update, name='maintenance_update'),
    path('<int:pk>/supprimer/', views.maintenance_delete, name='maintenance_delete'),
    path('<int:pk>/changer-statut/', views.maintenance_change_status, name='maintenance_change_status'),
    path('<int:pk>/envoyer-rappel/', views.maintenance_send_reminder, name='maintenance_send_reminder'),
    path('list/', views.maintenance_list, name='maintenance_list'),
]