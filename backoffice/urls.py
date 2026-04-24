from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('jugadores/', views.jugadores_lista, name='jugadores_lista'),
    path('jugadores/nuevo/', views.jugador_crear, name='jugador_crear'),
    path('jugadores/<int:pk>/editar/', views.jugador_editar, name='jugador_editar'),
    path('jugadores/<int:pk>/eliminar/', views.jugador_eliminar, name='jugador_eliminar'),
    path('sponsors/', views.sponsors_lista, name='sponsors_lista'),
    path('sponsors/<int:pk>/', views.sponsor_detalle, name='sponsor_detalle'),
    path('sponsors/<int:pk>/eliminar/', views.sponsor_eliminar, name='sponsor_eliminar'),
]
