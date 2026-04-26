"""
Exhaustive tests for Facebook reels facade, caching, and landing index.

Covers:
- Reels API: success, errors, filtering, encoding
- Caching: hit/miss, stores result, skips on error
- Facade: no live iframe on load, thumbnail, fallback, data-src
- iOS safety: no clipboard-write permission
- Landing index: status, context keys, partners, performance
"""
import json
import re
from io import BytesIO
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from backoffice.models import Partner
from landing.views import (
    _fetch_reels_from_api,
    _get_facebook_reels,
    _REELS_CACHE_KEY,
)

FB_SETTINGS = {
    'FB_PAGE_ID': '123456',
    'FB_PAGE_ACCESS_TOKEN': 'fake-token',
    'FB_GRAPH_API_VERSION': 'v25.0',
    'FB_REELS_LIMIT': 3,
    'FB_PAGE_URL': 'https://www.facebook.com/test',
    'FB_REELS_URL': 'https://www.facebook.com/test/reels/',
}

SAMPLE_REEL = {
    'id': '111',
    'permalink_url': 'https://www.facebook.com/reel/111/',
    'title': 'Test Reel',
    'picture': 'https://example.com/thumb.jpg',
    'description': 'A test reel',
    'created_time': '2026-01-01T00:00:00+0000',
    'format': [{'width': 9, 'height': 16}],
}

LANDSCAPE_REEL = {
    'id': '222',
    'permalink_url': 'https://www.facebook.com/reel/222/',
    'title': 'Landscape',
    'picture': '',
    'description': '',
    'created_time': '2026-01-01T00:00:00+0000',
    'format': [{'width': 16, 'height': 9}],
}


def _make_response(data):
    body = json.dumps(data).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ── API unit tests ────────────────────────────────────────────────

@override_settings(**FB_SETTINGS)
class FetchReelsFromApiTests(TestCase):

    def setUp(self):
        cache.clear()

    @patch('landing.views.urlopen')
    def test_returns_reels_on_success(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(
            {'data': [SAMPLE_REEL]}
        )
        reels = _fetch_reels_from_api()
        self.assertEqual(len(reels), 1)
        self.assertEqual(reels[0]['id'], '111')

    @patch('landing.views.urlopen')
    def test_filters_landscape_reels(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(
            {'data': [LANDSCAPE_REEL, SAMPLE_REEL]}
        )
        reels = _fetch_reels_from_api()
        self.assertEqual(len(reels), 1)
        self.assertEqual(reels[0]['id'], '111')

    @patch('landing.views.urlopen')
    def test_respects_reels_limit(self, mock_urlopen):
        many = [
            dict(
                SAMPLE_REEL,
                id=str(i),
                permalink_url=f'https://www.facebook.com/reel/{i}/',
            )
            for i in range(10)
        ]
        mock_urlopen.return_value = _make_response({'data': many})
        reels = _fetch_reels_from_api()
        self.assertLessEqual(len(reels), 3)

    @patch('landing.views.urlopen')
    def test_returns_none_on_api_error(self, mock_urlopen):
        mock_urlopen.return_value = _make_response(
            {'error': {'message': 'Token expired', 'code': 190}}
        )
        self.assertIsNone(_fetch_reels_from_api())

    @patch('landing.views.urlopen')
    def test_returns_none_on_url_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError('Network unreachable')
        self.assertIsNone(_fetch_reels_from_api())

    @patch('landing.views.urlopen')
    def test_returns_none_on_http_error(self, mock_urlopen):
        mock_urlopen.side_effect = HTTPError(
            url='https://graph.facebook.com',
            code=400,
            msg='Bad Request',
            hdrs=None,
            fp=BytesIO(b'{"error": {"code": 190}}'),
        )
        self.assertIsNone(_fetch_reels_from_api())

    @patch('landing.views.urlopen')
    def test_returns_none_on_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError()
        self.assertIsNone(_fetch_reels_from_api())

    @patch('landing.views.urlopen')
    def test_returns_none_on_malformed_json(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'not json {'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        self.assertIsNone(_fetch_reels_from_api())

    @patch('landing.views.urlopen')
    def test_relative_permalink_gets_domain_prepended(self, mock_urlopen):
        reel = dict(SAMPLE_REEL, permalink_url='/reel/999/')
        mock_urlopen.return_value = _make_response({'data': [reel]})
        reels = _fetch_reels_from_api()
        self.assertTrue(
            reels[0]['permalink_url'].startswith('https://www.facebook.com')
        )

    @patch('landing.views.urlopen')
    def test_reel_without_permalink_is_skipped(self, mock_urlopen):
        reel = dict(SAMPLE_REEL, permalink_url=None)
        mock_urlopen.return_value = _make_response({'data': [reel]})
        self.assertEqual(_fetch_reels_from_api(), [])

    @patch('landing.views.urlopen')
    def test_permalink_url_encoded_field_present(self, mock_urlopen):
        mock_urlopen.return_value = _make_response({'data': [SAMPLE_REEL]})
        reels = _fetch_reels_from_api()
        self.assertIn('permalink_url_encoded', reels[0])
        self.assertNotIn(' ', reels[0]['permalink_url_encoded'])


# ── Caching tests ─────────────────────────────────────────────────

@override_settings(**FB_SETTINGS)
class ReelsCacheTests(TestCase):

    def setUp(self):
        cache.clear()

    @patch('landing.views._fetch_reels_from_api')
    def test_cache_miss_calls_api(self, mock_fetch):
        mock_fetch.return_value = [{'id': '1'}]
        _get_facebook_reels()
        mock_fetch.assert_called_once()

    @patch('landing.views._fetch_reels_from_api')
    def test_cache_hit_skips_api(self, mock_fetch):
        cache.set(_REELS_CACHE_KEY, [{'id': 'cached'}])
        result = _get_facebook_reels()
        mock_fetch.assert_not_called()
        self.assertEqual(result[0]['id'], 'cached')

    @patch('landing.views._fetch_reels_from_api')
    def test_successful_result_is_cached(self, mock_fetch):
        mock_fetch.return_value = [{'id': 'fresh'}]
        _get_facebook_reels()
        cached = cache.get(_REELS_CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(cached[0]['id'], 'fresh')

    @patch('landing.views._fetch_reels_from_api')
    def test_api_error_returns_empty_list(self, mock_fetch):
        mock_fetch.return_value = None
        self.assertEqual(_get_facebook_reels(), [])

    @patch('landing.views._fetch_reels_from_api')
    def test_api_error_does_not_cache(self, mock_fetch):
        mock_fetch.return_value = None
        _get_facebook_reels()
        self.assertIsNone(cache.get(_REELS_CACHE_KEY))

    def test_returns_empty_list_when_no_page_id(self):
        with self.settings(FB_PAGE_ID='', FB_PAGE_ACCESS_TOKEN='token'):
            self.assertEqual(_get_facebook_reels(), [])

    def test_returns_empty_list_when_no_token(self):
        with self.settings(FB_PAGE_ID='123', FB_PAGE_ACCESS_TOKEN=''):
            self.assertEqual(_get_facebook_reels(), [])


# ── Template / facade pattern tests ──────────────────────────────

@override_settings(**FB_SETTINGS)
class ReelsFacadeTemplateTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('landing:index')
        cache.clear()

    @patch('landing.views._get_facebook_reels')
    def test_no_live_iframe_on_initial_load(self, mock_reels):
        """No <iframe src="...facebook..."> must exist on page load.
        The URL is in data-src (facade) but never in a live src."""
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        live_iframes = re.findall(
            rb'<iframe[^>]+src=["\'][^"\']*facebook[^"\']*["\']',
            res.content,
        )
        self.assertEqual(
            live_iframes, [],
            msg='Found a live Facebook iframe on initial page load',
        )

    @patch('landing.views._get_facebook_reels')
    def test_facade_card_has_data_src(self, mock_reels):
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        self.assertIn(b'fb-reel-facade', res.content)
        self.assertIn(b'data-src', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_data_src_contains_facebook_url(self, mock_reels):
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        self.assertIn(b'plugins/video.php', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_thumbnail_shown_when_picture_available(self, mock_reels):
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        self.assertIn(b'fb-reel-thumb', res.content)
        self.assertIn(b'https://example.com/thumb.jpg', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_fallback_shown_when_no_picture(self, mock_reels):
        mock_reels.return_value = [dict(SAMPLE_REEL, picture='')]
        res = self.client.get(self.url)
        self.assertIn(b'bi-facebook', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_no_clipboard_write_in_allow(self, mock_reels):
        """clipboard-write triggers iOS Safari permission popup — must be absent."""
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        self.assertNotIn(b'clipboard-write', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_empty_reels_shows_fallback_cards(self, mock_reels):
        mock_reels.return_value = []
        res = self.client.get(self.url)
        self.assertIn(b'fb-reel-card', res.content)

    @patch('landing.views._get_facebook_reels')
    def test_play_button_present_on_facade(self, mock_reels):
        mock_reels.return_value = [SAMPLE_REEL]
        res = self.client.get(self.url)
        self.assertIn(b'fb-reel-play', res.content)


# ── Landing index general tests ───────────────────────────────────

@override_settings(**FB_SETTINGS)
class LandingIndexTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('landing:index')
        cache.clear()

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_returns_200(self, _):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_context_has_required_keys(self, _):
        res = self.client.get(self.url)
        for key in (
            'facebook_reels', 'facebook_page_url',
            'facebook_reels_url', 'americas_choices', 'partners',
        ):
            self.assertIn(key, res.context)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_partners_only_shows_active(self, _):
        Partner.objects.create(
            nombre='Active', logo='partners/a.png', activo=True
        )
        Partner.objects.create(
            nombre='Inactive', logo='partners/b.png', activo=False
        )
        res = self.client.get(self.url)
        names = [p.nombre for p in res.context['partners']]
        self.assertIn('Active', names)
        self.assertNotIn('Inactive', names)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_partners_ordered_by_orden(self, _):
        Partner.objects.create(
            nombre='Second', logo='partners/b.png', orden=2, activo=True
        )
        Partner.objects.create(
            nombre='First', logo='partners/a.png', orden=1, activo=True
        )
        res = self.client.get(self.url)
        names = [p.nombre for p in res.context['partners']]
        self.assertEqual(names, ['First', 'Second'])

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_no_iframe_when_reels_empty(self, _):
        res = self.client.get(self.url)
        self.assertNotIn(b'plugins/video.php', res.content)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_page_loader_present(self, _):
        res = self.client.get(self.url)
        self.assertIn(b'page-loader', res.content)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_critical_dark_css_present(self, _):
        """Dark bg must be inline before stylesheets (prevents white flash)."""
        res = self.client.get(self.url)
        self.assertIn(b'background:#0a0a0a', res.content)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_favicon_present(self, _):
        res = self.client.get(self.url)
        self.assertIn(b'favicon.png', res.content)

    @patch('landing.views._get_facebook_reels', return_value=[])
    def test_exec_photos_have_lazy_loading(self, _):
        res = self.client.get(self.url)
        content = res.content.decode('utf-8')
        exec_imgs = re.findall(r'<img[^>]+exec-photo[^>]*>', content)
        non_lazy = [
            img for img in exec_imgs if 'loading="lazy"' not in img
        ]
        self.assertEqual(
            non_lazy, [],
            msg=f'exec-photo images missing loading=lazy: {non_lazy}',
        )
