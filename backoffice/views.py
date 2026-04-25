import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from jugadores.models import Jugador
from landing.models import SponsorInquiry, PageVisit
from .forms import JugadorForm

COUNTRY_NAMES = {
    'US': 'United States', 'MX': 'Mexico', 'DO': 'Dominican Republic',
    'CU': 'Cuba', 'VE': 'Venezuela', 'PR': 'Puerto Rico', 'PA': 'Panama',
    'CO': 'Colombia', 'NI': 'Nicaragua', 'HN': 'Honduras', 'GT': 'Guatemala',
    'SV': 'El Salvador', 'CR': 'Costa Rica', 'AR': 'Argentina', 'BR': 'Brazil',
    'CA': 'Canada', 'EC': 'Ecuador', 'PE': 'Peru', 'CL': 'Chile',
    'BO': 'Bolivia', 'UY': 'Uruguay', 'PY': 'Paraguay', 'JM': 'Jamaica',
    'HT': 'Haiti', 'TT': 'Trinidad and Tobago', 'ES': 'Spain', 'GB': 'UK',
    'DE': 'Germany', 'FR': 'France', 'IT': 'Italy', 'AU': 'Australia',
    'JP': 'Japan', 'LO': 'Local (dev)',
}


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
    if request.method == 'POST':
        logout(request)
    return redirect('backoffice:login')


@login_required
def dashboard(request):
    today = timezone.now().date()
    day30 = today - timedelta(days=29)
    day7  = today - timedelta(days=6)

    # ── Players ───────────────────────────────────────────────
    total_jugadores = Jugador.objects.count()
    doble_nac = Jugador.objects.filter(doble_nacionalidad=True).count()
    jugadores_hoy = Jugador.objects.filter(fecha_registro__date=today).count()
    recientes = Jugador.objects.order_by('-fecha_registro')[:5]

    jugadores_por_dia = list(
        Jugador.objects.filter(fecha_registro__date__gte=day30)
        .annotate(day=TruncDate('fecha_registro'))
        .values('day')
        .annotate(n=Count('id'))
        .order_by('day')
    )

    jugadores_por_pais = list(
        Jugador.objects.values('pais')
        .annotate(n=Count('id'))
        .order_by('-n')[:10]
    )

    # ── Sponsors ──────────────────────────────────────────────
    total_sponsors = SponsorInquiry.objects.count()
    sponsors_recientes = SponsorInquiry.objects.order_by('-fecha_registro')[:3]

    # ── Page visits ───────────────────────────────────────────
    total_visitas = PageVisit.objects.count()
    visitas_hoy = PageVisit.objects.filter(timestamp__date=today).count()
    visitas_semana = PageVisit.objects.filter(timestamp__date__gte=day7).count()
    visitantes_unicos = PageVisit.objects.values('ip').distinct().count()
    mobile_count  = PageVisit.objects.filter(is_mobile=True).count()
    desktop_count = total_visitas - mobile_count
    mobile_pct    = round(mobile_count * 100 / total_visitas) if total_visitas else 0
    desktop_pct   = 100 - mobile_pct

    visitas_por_dia = list(
        PageVisit.objects.filter(timestamp__date__gte=day30)
        .annotate(day=TruncDate('timestamp'))
        .values('day')
        .annotate(n=Count('id'))
        .order_by('day')
    )

    top_paises = list(
        PageVisit.objects
        .exclude(country_code='')
        .exclude(country_code='LO')
        .values('country_code')
        .annotate(n=Count('id'))
        .order_by('-n')[:12]
    )
    for row in top_paises:
        row['name'] = COUNTRY_NAMES.get(row['country_code'], row['country_code'])

    top_paginas = list(
        PageVisit.objects.values('path')
        .annotate(n=Count('id'))
        .order_by('-n')[:8]
    )

    # ── Build chart series (fill missing days with 0) ─────────
    def _fill_days(rows, start, days=30):
        by_date = {r['day']: r['n'] for r in rows}
        labels, data = [], []
        for i in range(days):
            d = start + timedelta(days=i)
            labels.append(f'{d.day} {d.strftime("%b")}')
            data.append(by_date.get(d, 0))
        return labels, data

    v_labels, v_data = _fill_days(visitas_por_dia, day30)
    j_labels, j_data = _fill_days(jugadores_por_dia, day30)

    return render(request, 'backoffice/dashboard.html', {
        # stats
        'total_jugadores': total_jugadores,
        'doble_nac': doble_nac,
        'jugadores_hoy': jugadores_hoy,
        'total_sponsors': total_sponsors,
        'total_visitas': total_visitas,
        'visitas_hoy': visitas_hoy,
        'visitas_semana': visitas_semana,
        'visitantes_unicos': visitantes_unicos,
        'mobile_pct': mobile_pct,
        'desktop_pct': desktop_pct,
        'mobile_count': mobile_count,
        'desktop_count': desktop_count,
        # tables
        'recientes': recientes,
        'sponsors_recientes': sponsors_recientes,
        'top_paises': top_paises,
        'top_paginas': top_paginas,
        'jugadores_por_pais': jugadores_por_pais,
        # chart data (JSON)
        'v_labels': json.dumps(v_labels),
        'v_data': json.dumps(v_data),
        'j_labels': json.dumps(j_labels),
        'j_data': json.dumps(j_data),
        'paises_labels': json.dumps([r['name'] for r in top_paises]),
        'paises_data': json.dumps([r['n'] for r in top_paises]),
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


@login_required
def sponsors_lista(request):
    q = request.GET.get('q', '')
    sponsors = SponsorInquiry.objects.all()
    if q:
        sponsors = sponsors.filter(
            Q(company_name__icontains=q) |
            Q(contact_name__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, 'backoffice/sponsors/lista.html', {
        'sponsors': sponsors,
        'q': q,
    })


@login_required
def sponsor_detalle(request, pk):
    sponsor = get_object_or_404(SponsorInquiry, pk=pk)
    return render(request, 'backoffice/sponsors/detalle.html', {
        'sponsor': sponsor,
    })


@login_required
def sponsor_eliminar(request, pk):
    sponsor = get_object_or_404(SponsorInquiry, pk=pk)
    if request.method == 'POST':
        sponsor.delete()
        messages.success(request, _('Sponsor inquiry deleted.'))
        return redirect('backoffice:sponsors_lista')
    return render(request, 'backoffice/sponsors/confirmar_eliminar.html', {
        'sponsor': sponsor,
    })
