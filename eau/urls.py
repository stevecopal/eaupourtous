from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView


urlpatterns = [
    path('', views.IndexView.as_view(), name='home'),
    path('realisations/', views.RealisationListView.as_view(), name='realisations'),
    path('realisations/<int:pk>/', views.RealisationDetailView.as_view(), name='realisation_detail'),
    path('api/realisations/', views.realisations_api, name='realisations_api'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    # auth
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

]