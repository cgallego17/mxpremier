import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from backoffice.forms import JugadorForm


logger = logging.getLogger(__name__)


def _get_facebook_reels():
    if not settings.FB_PAGE_ID or not settings.FB_PAGE_ACCESS_TOKEN:
        return []

    params = urlencode(
        {
            'fields': 'id,permalink_url,description,created_time',
            'limit': settings.FB_REELS_LIMIT,
            'access_token': settings.FB_PAGE_ACCESS_TOKEN,
        }
    )
    endpoint = (
        'https://graph.facebook.com/'
        f'{settings.FB_GRAPH_API_VERSION}/{settings.FB_PAGE_ID}/video_reels?{params}'
    )
    request = Request(endpoint, headers={'Accept': 'application/json'})

    try:
        with urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning('Unable to fetch Facebook reels: %s', exc)
        return []

    if payload.get('error'):
        logger.warning('Facebook reels API returned an error: %s', payload['error'])
        return []

    reels = []
    for item in payload.get('data', []):
        permalink_url = item.get('permalink_url')
        if not permalink_url:
            continue
        reels.append(
            {
                'id': item.get('id', ''),
                'permalink_url': permalink_url,
                'description': item.get('description', ''),
                'created_time': item.get('created_time', ''),
            }
        )
        if len(reels) >= settings.FB_REELS_LIMIT:
            break
    return reels


def index(request):
    context = {
        'facebook_reels': _get_facebook_reels(),
        'facebook_page_url': settings.FB_PAGE_URL,
        'facebook_reels_url': settings.FB_REELS_URL,
    }
    return render(request, 'landing/index.html', context)


@require_POST
def registro(request):
    form = JugadorForm(request.POST)
    if form.is_valid():
        jugador = form.save(commit=False)
        if not jugador.email and jugador.tutor_email:
            jugador.email = jugador.tutor_email
        jugador.save()
        return JsonResponse({'ok': True})
    return JsonResponse({'ok': False, 'errors': form.errors}, status=400)
