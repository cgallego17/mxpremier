from django.http import JsonResponse
from jugadores.models import Pais, Estado, Ciudad


def paises_json(request):
    """Return all countries ordered by baseball relevance."""
    paises = (
        Pais.objects
        .values('codigo', 'nombre', 'orden')
        .order_by('orden', 'nombre')
    )
    return JsonResponse({'paises': list(paises)})


def estados_json(request):
    """Return states/provinces for a given country code."""
    pais_codigo = request.GET.get('pais', '').strip()
    if not pais_codigo:
        return JsonResponse({'estados': []})
    estados = (
        Estado.objects
        .filter(pais__codigo=pais_codigo)
        .values('codigo', 'nombre')
        .order_by('nombre')
    )
    return JsonResponse({'estados': list(estados)})


def ciudades_json(request):
    """Return cities for a given country + state code."""
    pais_codigo = request.GET.get('pais', '').strip()
    estado_codigo = request.GET.get('estado', '').strip()
    if not pais_codigo or not estado_codigo:
        return JsonResponse({'ciudades': []})
    ciudades = (
        Ciudad.objects
        .filter(estado__codigo=estado_codigo, estado__pais__codigo=pais_codigo)
        .values_list('nombre', flat=True)
        .order_by('nombre')
    )
    return JsonResponse({'ciudades': list(ciudades)})

