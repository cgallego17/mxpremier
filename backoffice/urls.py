from django.urls import path
from . import views

app_name = 'backoffice'

_j = 'jugadores'
_s = 'sponsors'
_p = 'partners'
_g = 'gastos'

urlpatterns = [
    path('login/',   views.login_view,  name='login'),
    path('logout/',  views.logout_view, name='logout'),
    path('',         views.dashboard,   name='dashboard'),

    # Players
    path(f'{_j}/',                   views.jugadores_lista,    name='jugadores_lista'),
    path(f'{_j}/nuevo/',             views.jugador_crear,      name='jugador_crear'),
    path(f'{_j}/exportar/',          views.jugadores_exportar, name='jugadores_exportar'),
    path(f'{_j}/<int:pk>/',          views.jugador_detalle,    name='jugador_detalle'),
    path(f'{_j}/<int:pk>/editar/',   views.jugador_editar,     name='jugador_editar'),
    path(f'{_j}/<int:pk>/eliminar/', views.jugador_eliminar,   name='jugador_eliminar'),

    # Sponsors
    path(f'{_s}/',                   views.sponsors_lista,    name='sponsors_lista'),
    path(f'{_s}/exportar/',          views.sponsors_exportar, name='sponsors_exportar'),
    path(f'{_s}/<int:pk>/',          views.sponsor_detalle,   name='sponsor_detalle'),
    path(f'{_s}/<int:pk>/eliminar/', views.sponsor_eliminar,  name='sponsor_eliminar'),

    # Partners
    path(f'{_p}/',                   views.partners_lista,   name='partners_lista'),
    path(f'{_p}/nuevo/',             views.partner_crear,    name='partner_crear'),
    path(f'{_p}/<int:pk>/editar/',   views.partner_editar,   name='partner_editar'),
    path(f'{_p}/<int:pk>/eliminar/', views.partner_eliminar, name='partner_eliminar'),

    # Gastos
    path(f'{_g}/',                   views.gastos_lista,     name='gastos_lista'),
    path(f'{_g}/nuevo/',             views.gasto_crear,      name='gasto_crear'),
    path(f'{_g}/exportar/',          views.gastos_exportar,  name='gastos_exportar'),
    path(f'{_g}/<int:pk>/editar/',   views.gasto_editar,     name='gasto_editar'),
    path(f'{_g}/<int:pk>/eliminar/', views.gasto_eliminar,   name='gasto_eliminar'),
]
