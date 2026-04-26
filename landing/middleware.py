import json
from urllib.request import urlopen
from urllib.error import URLError
from django.core.cache import cache

_SKIP = (
    '/backoffice/', '/admin/', '/static/', '/media/',
    '/i18n/', '/registro/', '/sponsor/',
)

_TABLET_HINTS = ('ipad', 'tablet', 'kindle', 'silk', 'playbook', 'xoom', 'sm-t', 'gt-p')
_MOBILE_HINTS = ('mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone', 'webos')
_PRIVATE = ('127.', '192.168.', '10.', '172.', '169.254.', '100.64.', 'fc', 'fd')


def _get_ip(request):
    for header in ('HTTP_CF_CONNECTING_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'):
        value = request.META.get(header, '')
        if value:
            return value.split(',')[0].strip()
    return ''


def _get_device_type(ua):
    ua_lower = ua.lower()
    if any(k in ua_lower for k in _TABLET_HINTS):
        return 'tablet'
    if any(k in ua_lower for k in _MOBILE_HINTS):
        return 'mobile'
    return 'desktop'


def _is_private(ip):
    return (
        not ip
        or ip in ('::1', '0.0.0.0')
        or any(ip.startswith(p) for p in _PRIVATE)
    )


def _get_geo(request, ip):
    """Return dict with country_code, region, city."""
    cf_country = request.META.get('HTTP_CF_IPCOUNTRY', '')
    if cf_country and cf_country not in ('XX', ''):
        cf_country = cf_country.upper()[:2]
    else:
        cf_country = ''
        for hdr in ('HTTP_X_COUNTRY_CODE', 'HTTP_GEOIP_COUNTRY_CODE'):
            val = request.META.get(hdr, '')
            if val:
                cf_country = val.upper()[:2]
                break

    if _is_private(ip):
        return {'country_code': 'LO', 'region': '', 'city': ''}

    key = f'geoip2_{ip}'
    cached = cache.get(key)
    if cached is not None:
        if cf_country:
            cached['country_code'] = cf_country
        return cached

    try:
        url = f'http://ip-api.com/json/{ip}?fields=countryCode,regionName,city'
        with urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read().decode())
        result = {
            'country_code': (cf_country or data.get('countryCode', ''))[:2].upper(),
            'region': data.get('regionName', '')[:100],
            'city': data.get('city', '')[:100],
        }
    except (URLError, OSError, ValueError):
        result = {'country_code': cf_country, 'region': '', 'city': ''}

    cache.set(key, result, timeout=86400)
    return result


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
                geo = _get_geo(request, ip)
                device = _get_device_type(ua)
                PageVisit.objects.create(
                    ip=ip[:45],
                    path=request.path[:200],
                    user_agent=ua,
                    country_code=geo['country_code'],
                    region=geo['region'],
                    city=geo['city'],
                    referrer=request.META.get('HTTP_REFERER', '')[:300],
                    is_mobile=(device == 'mobile'),
                    device_type=device,
                )
            except Exception:
                pass

        return response
