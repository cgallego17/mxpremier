import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from backoffice.forms import JugadorForm
from backoffice.models import Partner
from jugadores.choices import AMERICAS_CHOICES
from landing.forms import SponsorForm


logger = logging.getLogger(__name__)


def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _is_rate_limited(ip):
    limit = getattr(settings, 'REGISTRO_RATE_LIMIT', 5)
    window = getattr(settings, 'REGISTRO_RATE_WINDOW', 3600)
    key = f'reg_rate_{ip}'
    count = cache.get(key, 0)
    if count >= limit:
        return True
    cache.set(key, count + 1, timeout=window)
    return False


_REELS_CACHE_KEY = 'fb_reels_v1'
_REELS_CACHE_TTL = 900  # 15 minutos


def _fetch_reels_from_api():
    params = urlencode(
        {
            'fields': (
                'id,permalink_url,title,picture,'
                'format,description,created_time'
            ),
            'limit': settings.FB_REELS_LIMIT * 4,
            'access_token': settings.FB_PAGE_ACCESS_TOKEN,
        }
    )
    endpoint = (
        'https://graph.facebook.com/'
        f'{settings.FB_GRAPH_API_VERSION}'
        f'/{settings.FB_PAGE_ID}/video_reels?{params}'
    )
    request = Request(endpoint, headers={'Accept': 'application/json'})

    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning('Unable to fetch Facebook reels: %s', exc)
        return None

    if payload.get('error'):
        logger.warning('Facebook reels API error: %s', payload['error'])
        return None

    reels = []
    for item in payload.get('data', []):
        permalink_url = item.get('permalink_url')
        if not permalink_url:
            continue
        fmt = (item.get('format') or [{}])[0]
        if fmt.get('width', 0) > fmt.get('height', 1):
            continue
        if permalink_url.startswith('/'):
            permalink_url = f'https://www.facebook.com{permalink_url}'
        reels.append(
            {
                'id': item.get('id', ''),
                'permalink_url': permalink_url,
                'permalink_url_encoded': quote(permalink_url, safe=''),
                'title': item.get('title', ''),
                'picture': item.get('picture', ''),
                'description': item.get('description', ''),
                'created_time': item.get('created_time', ''),
            }
        )
        if len(reels) >= settings.FB_REELS_LIMIT:
            break
    return reels


def _get_facebook_reels():
    if not settings.FB_PAGE_ID or not settings.FB_PAGE_ACCESS_TOKEN:
        return []

    cached = cache.get(_REELS_CACHE_KEY)
    if cached is not None:
        return cached

    reels = _fetch_reels_from_api()
    if reels is None:
        return []

    cache.set(_REELS_CACHE_KEY, reels, timeout=_REELS_CACHE_TTL)
    return reels


def index(request):
    context = {
        'facebook_reels': _get_facebook_reels(),
        'facebook_page_url': settings.FB_PAGE_URL,
        'facebook_reels_url': settings.FB_REELS_URL,
        'americas_choices': AMERICAS_CHOICES,
        'partners': Partner.objects.filter(activo=True),
    }
    return render(request, 'landing/index.html', context)


@require_POST
def registro(request):
    ip = _get_client_ip(request)
    if _is_rate_limited(ip):
        return JsonResponse(
            {'ok': False, 'error': 'too_many_requests'}, status=429
        )
    form = JugadorForm(request.POST)
    if form.is_valid():
        jugador = form.save(commit=False)
        if not jugador.email and jugador.tutor_email:
            jugador.email = jugador.tutor_email
        jugador.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)


@require_POST
def sponsor(request):
    ip = _get_client_ip(request)
    if _is_rate_limited(ip):
        return JsonResponse(
            {'ok': False, 'error': 'too_many_requests'}, status=429
        )
    form = SponsorForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
