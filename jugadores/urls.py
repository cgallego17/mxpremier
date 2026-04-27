from django.urls import path
from . import views

urlpatterns = [
    path('paises/', views.paises_json, name='location_paises'),
    path('estados/', views.estados_json, name='location_estados'),
    path('ciudades/', views.ciudades_json, name='location_ciudades'),
]
