import json
from urllib.request import urlopen
from urllib.error import URLError
from django.core.cache import cache

_SKIP = ('/backoffice/', '/admin/', '/static/', '/media/', '/i18n/', '/registro/', '/sponsor/')
_MOBILE_HINTS = ('mobile', 'android', 'iphone', 'ipad', 'tablet', 'phone')


def _get_ip(request):
    for header in ('HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'):
        value = request.META.get(header, '')
        if value:
            return value.split(',')[0].strip()
    return ''


def _get_country(request, ip):
    cf = request.META.get('HTTP_CF_IPCOUNTRY', '')
    if cf and cf not in ('XX', ''):
        return cf.upper()[:2]

    for hdr in ('HTTP_X_COUNTRY_CODE', 'HTTP_GEOIP_COUNTRY_CODE'):
        val = request.META.get(hdr, '')
        if val:
            return val.upper()[:2]

    _private = ('127.', '192.168.', '10.', '172.', '169.254.', '100.64.', 'fc', 'fd')
    if not ip or ip.startswith(_private) or ip in ('::1', '0.0.0.0'):
        return 'LO'

    key = f'geoip_{ip}'
    cached = cache.get(key)
    if cached is not None:
        return cached

    try:
        url = f'http://ip-api.com/json/{ip}?fields=countryCode'
        with urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read().decode())
        country = data.get('countryCode', '')[:2].upper()
    except (URLError, OSError, ValueError):
        country = ''

    cache.set(key, country, timeout=86400)
    return country


class VisitTrackingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if (request.method == 'GET'
                and response.status_code == 200
                and not any(request.path.startswith(p) for p in _SKIP)):
            try:
                from landing.models import PageVisit
                ip = _get_ip(request)
                ua = request.META.get('HTTP_USER_AGENT', '')[:300]
                PageVisit.objects.create(
                    ip=ip[:45],
                    path=request.path[:200],
                    user_agent=ua,
                    country_code=_get_country(request, ip),
                    referrer=request.META.get('HTTP_REFERER', '')[:300],
                    is_mobile=any(k in ua.lower() for k in _MOBILE_HINTS),
                )
            except Exception:
                pass

        return response
