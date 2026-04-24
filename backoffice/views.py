from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from jugadores.models import Jugador
from .forms import JugadorForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('backoffice:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('backoffice:dashboard')
        messages.error(request, _('Invalid username or password.'))
    return render(request, 'backoffice/login.html')


def logout_view(request):
    logout(request)
    return redirect('backoffice:login')


@login_required
def dashboard(request):
    total = Jugador.objects.count()
    doble_nac = Jugador.objects.filter(doble_nacionalidad=True).count()
    recientes = Jugador.objects.order_by('-fecha_registro')[:5]
    return render(request, 'backoffice/dashboard.html', {
        'total': total,
        'doble_nac': doble_nac,
        'recientes': recientes,
    })


@login_required
def jugadores_lista(request):
    q = request.GET.get('q', '')
    jugadores = Jugador.objects.all()
    if q:
        jugadores = jugadores.filter(
            Q(nombre__icontains=q) |
            Q(apellidos__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, 'backoffice/jugadores/lista.html', {
        'jugadores': jugadores,
        'q': q,
    })


@login_required
def jugador_crear(request):
    form = JugadorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Player registered successfully.'))
        return redirect('backoffice:jugadores_lista')
    return render(request, 'backoffice/jugadores/form.html', {
        'form': form,
        'titulo': _('New Player'),
    })


@login_required
def jugador_editar(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk)
    form = JugadorForm(request.POST or None, instance=jugador)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, _('Player updated successfully.'))
        return redirect('backoffice:jugadores_lista')
    return render(request, 'backoffice/jugadores/form.html', {
        'form': form,
        'titulo': _('Edit') + f' — {jugador}',
        'jugador': jugador,
    })


@login_required
def jugador_eliminar(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk)
    if request.method == 'POST':
        jugador.delete()
        messages.success(request, _('Player deleted.'))
        return redirect('backoffice:jugadores_lista')
    return render(request, 'backoffice/jugadores/confirmar_eliminar.html', {
        'jugador': jugador,
    })
