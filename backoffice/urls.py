from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    path('login/',   views.login_view,  name='login'),
    path('logout/',  views.logout_view, name='logout'),
    path('',         views.dashboard,   name='dashboard'),

    # Players
    path('jugadores/',                   views.jugadores_lista,  name='jugadores_lista'),
    path('jugadores/nuevo/',             views.jugador_crear,    name='jugador_crear'),
    path('jugadores/<int:pk>/editar/',   views.jugador_editar,   name='jugador_editar'),
    path('jugadores/<int:pk>/eliminar/', views.jugador_eliminar, name='jugador_eliminar'),

    # Sponsors
    path('sponsors/',                    views.sponsors_lista,   name='sponsors_lista'),
    path('sponsors/<int:pk>/',           views.sponsor_detalle,  name='sponsor_detalle'),
    path('sponsors/<int:pk>/eliminar/',  views.sponsor_eliminar, name='sponsor_eliminar'),

    # Partners
    path('partners/',                    views.partners_lista,   name='partners_lista'),
    path('partners/nuevo/',              views.partner_crear,    name='partner_crear'),
    path('partners/<int:pk>/editar/',    views.partner_editar,   name='partner_editar'),
    path('partners/<int:pk>/eliminar/',  views.partner_eliminar, name='partner_eliminar'),

    # Gastos
    path('gastos/',                      views.gastos_lista,     name='gastos_lista'),
    path('gastos/nuevo/',                views.gasto_crear,      name='gasto_crear'),
    path('gastos/exportar/',             views.gastos_exportar,  name='gastos_exportar'),
    path('gastos/<int:pk>/editar/',      views.gasto_editar,     name='gasto_editar'),
    path('gastos/<int:pk>/eliminar/',    views.gasto_eliminar,   name='gasto_eliminar'),
]
