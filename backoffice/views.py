import csv
import json
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from .excel import build_workbook, wb_to_response, workbook_response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from jugadores.models import Jugador
from jugadores.choices import AMERICAS_CHOICES
from landing.models import SponsorInquiry, PageVisit
from .forms import JugadorForm, GastoForm, PartnerForm
from .models import Partner, Gasto, CATEGORIA_COLORS, CATEGORIAS_GASTO

COUNTRY_NAMES = {
    'US': 'United States', 'MX': 'Mexico', 'DO': 'Dominican Republic',
    'CU': 'Cuba', 'VE': 'Venezuela', 'PR': 'Puerto Rico', 'PA': 'Panama',
    'CO': 'Colombia', 'NI': 'Nicaragua', 'HN': 'Honduras',
    'GT': 'Guatemala', 'SV': 'El Salvador', 'CR': 'Costa Rica',
    'AR': 'Argentina', 'BR': 'Brazil', 'CA': 'Canada', 'EC': 'Ecuador',
    'PE': 'Peru', 'CL': 'Chile', 'BO': 'Bolivia', 'UY': 'Uruguay',
    'PY': 'Paraguay', 'JM': 'Jamaica', 'HT': 'Haiti',
    'TT': 'Trinidad and Tobago', 'ES': 'Spain', 'GB': 'UK',
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
    day7 = today - timedelta(days=6)

    # ── Players ───────────────────────────────────────────────────
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

    # Age distribution from registered players
    edades_raw = list(
        Jugador.objects.exclude(edad__isnull=True)
        .values('edad')
        .annotate(n=Count('id'))
        .order_by('edad')
    )
    edades_labels = [str(r['edad']) for r in edades_raw]
    edades_data = [r['n'] for r in edades_raw]

    # ── Expenses ──────────────────────────────────────────────────
    from django.db.models import Sum as _Sum
    total_gastos_usd = (
        Gasto.objects.filter(moneda='USD', estado__in=['pendiente', 'pagado'])
        .aggregate(t=_Sum('monto'))['t'] or 0
    )
    gastos_pendientes = Gasto.objects.filter(estado='pendiente').count()

    # ── Sponsors ──────────────────────────────────────────────────
    total_sponsors = SponsorInquiry.objects.count()
    sponsors_recientes = SponsorInquiry.objects.order_by('-fecha_registro')[:3]

    # ── Page visits ───────────────────────────────────────────────
    total_visitas = PageVisit.objects.count()
    visitas_hoy = PageVisit.objects.filter(timestamp__date=today).count()
    visitas_semana = PageVisit.objects.filter(
        timestamp__date__gte=day7
    ).count()
    visitantes_unicos = PageVisit.objects.values('ip').distinct().count()

    # Device breakdown (mobile / tablet / desktop)
    device_counts = {
        r['device_type']: r['n']
        for r in PageVisit.objects
        .values('device_type')
        .annotate(n=Count('id'))
    }
    mobile_count = device_counts.get('mobile', 0)
    tablet_count = device_counts.get('tablet', 0)
    desktop_count = device_counts.get('desktop', 0)
    if total_visitas:
        mobile_pct = round(mobile_count * 100 / total_visitas)
        tablet_pct = round(tablet_count * 100 / total_visitas)
        desktop_pct = 100 - mobile_pct - tablet_pct
    else:
        mobile_pct = tablet_pct = desktop_pct = 0

    # Fallback: old rows without device_type use is_mobile
    if not any(device_counts.values()):
        mobile_count = PageVisit.objects.filter(is_mobile=True).count()
        desktop_count = total_visitas - mobile_count
        tablet_count = 0
        mobile_pct = (
            round(mobile_count * 100 / total_visitas) if total_visitas else 0
        )
        desktop_pct = 100 - mobile_pct
        tablet_pct = 0

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

    # Top states / regions
    top_estados = list(
        PageVisit.objects
        .exclude(region='')
        .values('region')
        .annotate(n=Count('id'))
        .order_by('-n')[:10]
    )

    # Top cities
    top_ciudades = list(
        PageVisit.objects
        .exclude(city='')
        .values('city', 'region')
        .annotate(n=Count('id'))
        .order_by('-n')[:10]
    )

    top_paginas = list(
        PageVisit.objects.values('path')
        .annotate(n=Count('id'))
        .order_by('-n')[:8]
    )

    # ── Chart series (fill missing days with 0) ───────────────────
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
        'total_gastos_usd': total_gastos_usd,
        'gastos_pendientes': gastos_pendientes,
        'total_jugadores': total_jugadores,
        'doble_nac': doble_nac,
        'jugadores_hoy': jugadores_hoy,
        'total_sponsors': total_sponsors,
        'total_visitas': total_visitas,
        'visitas_hoy': visitas_hoy,
        'visitas_semana': visitas_semana,
        'visitantes_unicos': visitantes_unicos,
        # device
        'mobile_pct': mobile_pct,
        'tablet_pct': tablet_pct,
        'desktop_pct': desktop_pct,
        'mobile_count': mobile_count,
        'tablet_count': tablet_count,
        'desktop_count': desktop_count,
        # tables
        'recientes': recientes,
        'sponsors_recientes': sponsors_recientes,
        'top_paises': top_paises,
        'top_paginas': top_paginas,
        'top_estados': top_estados,
        'top_ciudades': top_ciudades,
        'jugadores_por_pais': jugadores_por_pais,
        # chart data (JSON)
        'v_labels': json.dumps(v_labels),
        'v_data': json.dumps(v_data),
        'j_labels': json.dumps(j_labels),
        'j_data': json.dumps(j_data),
        'paises_labels': json.dumps([r['name'] for r in top_paises]),
        'paises_data': json.dumps([r['n'] for r in top_paises]),
        'edades_labels': json.dumps(edades_labels),
        'edades_data': json.dumps(edades_data),
    })


@login_required
def jugadores_lista(request):
    q = request.GET.get('q', '')
    jugadores = Jugador.objects.all()
    if q:
        jugadores = jugadores.filter(
            Q(nombre__icontains=q)
            | Q(apellidos__icontains=q)
            | Q(email__icontains=q)
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
            Q(company_name__icontains=q)
            | Q(contact_name__icontains=q)
            | Q(email__icontains=q)
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


# ── Partners ──────────────────────────────────────────────────────

@login_required
def partners_lista(request):
    partners = Partner.objects.all()
    return render(
        request, 'backoffice/partners/lista.html', {'partners': partners}
    )


@login_required
def partner_crear(request):
    form = PartnerForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, _('Partner added.'))
        return redirect('backoffice:partners_lista')
    return render(request, 'backoffice/partners/form.html', {
        'form': form,
        'titulo': _('Add Partner'),
    })


@login_required
def partner_editar(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    form = PartnerForm(
        request.POST or None, request.FILES or None, instance=partner
    )
    if form.is_valid():
        form.save()
        messages.success(request, _('Partner updated.'))
        return redirect('backoffice:partners_lista')
    return render(request, 'backoffice/partners/form.html', {
        'form': form,
        'titulo': _('Edit Partner'),
        'partner': partner,
    })


@login_required
def partner_eliminar(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        partner.logo.delete(save=False)
        partner.delete()
        messages.success(request, _('Partner deleted.'))
        return redirect('backoffice:partners_lista')
    return render(
        request,
        'backoffice/partners/confirmar_eliminar.html',
        {'partner': partner},
    )


# ── Gastos ────────────────────────────────────────────────────────


import traceback
from django.http import HttpResponse

@login_required
def gastos_lista(request):
    try:
        qs = Gasto.objects.all()

        # Filters
        categoria = request.GET.get('categoria', '')
        estado = request.GET.get('estado', '')
        moneda = request.GET.get('moneda', '')
        q = request.GET.get('q', '')

        if categoria:
            qs = qs.filter(categoria=categoria)
        if estado:
            qs = qs.filter(estado=estado)
        if moneda:
            qs = qs.filter(moneda=moneda)
        if q:
            qs = qs.filter(Q(titulo__icontains=q) | Q(notas__icontains=q))

        # Summary totals (unfiltered by currency for full picture)
        total_usd = (
            Gasto.objects.filter(moneda='USD', estado__in=['pendiente', 'pagado'])
            .aggregate(t=Sum('monto'))['t'] or 0
        )
        total_mxn = (
            Gasto.objects.filter(moneda='MXN', estado__in=['pendiente', 'pagado'])
            .aggregate(t=Sum('monto'))['t'] or 0
        )
        pagado_usd = (
            Gasto.objects.filter(moneda='USD', estado='pagado')
            .aggregate(t=Sum('monto'))['t'] or 0
        )
        pendiente_usd = (
            Gasto.objects.filter(moneda='USD', estado='pendiente')
            .aggregate(t=Sum('monto'))['t'] or 0
        )

        # By category chart data (USD only for simplicity)
        por_categoria = list(
            Gasto.objects.filter(moneda='USD', estado__in=['pendiente', 'pagado'])
            .values('categoria')
            .annotate(total=Sum('monto'))
            .order_by('-total')
        )
        cat_labels = [str(dict(CATEGORIAS_GASTO).get(r['categoria'], r['categoria'])) for r in por_categoria]
        cat_data = [float(r['total']) for r in por_categoria]
        cat_colors = [CATEGORIA_COLORS.get(r['categoria'], '#374151') for r in por_categoria]

        return render(request, 'backoffice/gastos/lista.html', {
            'gastos': qs,
            'total_usd': total_usd,
            'total_mxn': total_mxn,
            'pagado_usd': pagado_usd,
            'pendiente_usd': pendiente_usd,
            'categorias': CATEGORIAS_GASTO,
            'filtro_categoria': categoria,
            'filtro_estado': estado,
            'filtro_moneda': moneda,
            'q': q,
            'cat_labels': json.dumps(cat_labels),
            'cat_data': json.dumps(cat_data),
            'cat_colors': json.dumps(cat_colors),
        })
    except Exception as e:
        tb = traceback.format_exc()
        return HttpResponse(f'<h2>Error en gastos_lista</h2><pre>{tb}</pre>', status=500)


@login_required
def gasto_crear(request):
    form = GastoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, _('Expense saved.'))
        return redirect('backoffice:gastos_lista')
    return render(request, 'backoffice/gastos/form.html', {
        'form': form,
        'titulo': _('New Expense'),
    })


@login_required
def gasto_editar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    form = GastoForm(
        request.POST or None, request.FILES or None, instance=gasto
    )
    if form.is_valid():
        form.save()
        messages.success(request, _('Expense updated.'))
        return redirect('backoffice:gastos_lista')
    # Si el formulario no es válido, mostrar errores de depuración
    debug_errors = None
    if request.method == 'POST' and not form.is_valid():
        debug_errors = f"<pre>{form.errors.as_json()}</pre>"
    return render(request, 'backoffice/gastos/form.html', {
        'form': form,
        'gasto': gasto,
        'titulo': _('Edit Expense'),
        'debug_errors': debug_errors,
    })


@login_required
def gasto_eliminar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        if gasto.comprobante:
            gasto.comprobante.delete(save=False)
        gasto.delete()
        messages.success(request, _('Expense deleted.'))
        return redirect('backoffice:gastos_lista')
    return render(request, 'backoffice/gastos/confirmar_eliminar.html', {
        'gasto': gasto,
    })


@login_required
def jugadores_exportar(request):
    qs = Jugador.objects.all().order_by('apellidos', 'nombre')
    headers = [
        'First name', 'Last names', 'Date of birth', 'Age',
        'Country', 'State', 'City', 'Nationality', 'Dual nationality',
        'Email', 'Phone', 'Instagram',
        'Travel team', 'Team country', 'Team state', 'Team city',
        'Primary position', 'Secondary position', 'Pitcher',
        'Guardian name', 'Guardian email', 'Guardian phone',
        'Registered',
    ]
    rows = []
    for j in qs:
        rows.append([
            j.nombre, j.apellidos,
            j.fecha_nacimiento.strftime('%Y-%m-%d') if j.fecha_nacimiento else '',
            j.edad or '',
            j.get_pais_display(), j.estado, j.ciudad,
            j.get_nacionalidad_display(),
            'Yes' if j.doble_nacionalidad else 'No',
            j.email, j.telefono,
            f'@{j.instagram}' if j.instagram else '',
            j.equipo_viaje,
            j.get_equipo_pais_display(),
            j.equipo_estado,
            j.equipo_ciudad,
            j.get_posicion_principal_display() if j.posicion_principal else '',
            j.get_posicion_secundaria_display() if j.posicion_secundaria else '',
            'Yes' if j.es_pitcher else 'No',
            f'{j.tutor_nombre} {j.tutor_apellidos}'.strip(),
            j.tutor_email, j.tutor_telefono,
            j.fecha_registro.strftime('%Y-%m-%d %H:%M'),
        ])
    col_widths = [
        14, 18, 14, 5,
        14, 14, 14, 14, 8,
        26, 14, 14,
        22, 14, 14, 14,
        16, 16, 7,
        22, 26, 14,
        18,
    ]
    wb, _ = build_workbook('Player Registrations', headers, rows, col_widths)
    resp = workbook_response('jugadores_estado33.xlsx')
    return wb_to_response(wb, resp)


@login_required
def sponsors_exportar(request):
    qs = SponsorInquiry.objects.all().order_by('-fecha_registro')
    headers = [
        'Company', 'Contact', 'Email', 'Phone', 'Website',
        'Budget', 'Wants proposal',
        'Teams', 'Players', 'Showcases', 'Tournaments', 'Full program',
        'Brand awareness', 'Support youth', 'Community',
        'Marketing', 'Intl. reach',
        'Logo on uniforms', 'Event branding', 'Social media', 'On-site',
        'Notes', 'Submitted',
    ]
    rows = []
    for s in qs:
        rows.append([
            s.company_name, s.contact_name, s.email,
            s.phone, s.website,
            s.get_budget_display() if s.budget else '',
            'Yes' if s.wants_proposal        else 'No',
            'Yes' if s.interest_teams        else 'No',
            'Yes' if s.interest_players      else 'No',
            'Yes' if s.interest_showcases    else 'No',
            'Yes' if s.interest_tournaments  else 'No',
            'Yes' if s.interest_full_program else 'No',
            'Yes' if s.goal_brand_awareness  else 'No',
            'Yes' if s.goal_youth_athletes   else 'No',
            'Yes' if s.goal_community        else 'No',
            'Yes' if s.goal_marketing        else 'No',
            'Yes' if s.goal_international    else 'No',
            'Yes' if s.activation_logo       else 'No',
            'Yes' if s.activation_event      else 'No',
            'Yes' if s.activation_social     else 'No',
            'Yes' if s.activation_onsite     else 'No',
            s.notes,
            s.fecha_registro.strftime('%Y-%m-%d %H:%M'),
        ])
    col_widths = [
        22, 20, 26, 14, 26,
        16, 8,
        7, 7, 7, 7, 7,
        7, 7, 7, 7, 7,
        7, 7, 7, 7,
        30, 18,
    ]
    wb, _ = build_workbook('Sponsor Inquiries', headers, rows, col_widths)
    resp = workbook_response('sponsors_estado33.xlsx')
    return wb_to_response(wb, resp)


@login_required
def gastos_exportar(request):
    qs = Gasto.objects.all().order_by('-fecha')
    cat_display = dict(CATEGORIAS_GASTO)
    headers = [
        'Date', 'Title', 'Category', 'Amount', 'Currency',
        'Payment method', 'Status', 'Notes', 'Registered',
    ]
    import traceback
    rows = []
    try:
        for g in qs:
            try:
                row = [
                    str(g.fecha.strftime('%Y-%m-%d')) if g.fecha else 'N/A',
                    str(g.titulo),
                    str(cat_display.get(g.categoria, g.categoria)),
                    float(g.monto) if g.monto is not None else 0.0,
                    str(g.moneda),
                    str(g.get_metodo_pago_display()),
                    str(g.get_estado_display()),
                    str(g.notas) if g.notas is not None else '',
                    str(g.fecha_registro.strftime('%Y-%m-%d %H:%M')) if g.fecha_registro else 'N/A',
                ]
                rows.append(row)
            except Exception as row_exc:
                return HttpResponse(f'<h2>Error en gasto ID {g.id}</h2><pre>{traceback.format_exc()}</pre>', status=500)
        col_widths = [12, 30, 16, 12, 8, 14, 12, 36, 18]
        wb, _ = build_workbook('Expenses', headers, rows, col_widths)
        resp = workbook_response('gastos_estado33.xlsx')
        return wb_to_response(wb, resp)
    except Exception as exc:
        return HttpResponse(f'<h2>Error general en gastos_exportar</h2><pre>{traceback.format_exc()}</pre>', status=500)
