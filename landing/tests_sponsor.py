from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from landing.models import SponsorInquiry  # pylint: disable=no-member


VALID_DATA = {
    'company_name': 'Acme Corp',
    'contact_name': 'Jane Smith',
    'email': 'jane@acme.com',
    'phone': '+1 555-123-4567',
    'website': 'https://acme.com',
    'budget': '5k_10k',
    'interest_teams': True,
    'goal_brand_awareness': True,
    'activation_social': True,
    'notes': 'Interested in jersey branding.',
    'wants_proposal': 'True',
}


class SponsorViewTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = reverse('landing:sponsor')
        cache.clear()

    # ── Happy path ──────────────────────────────────────────────────────

    def test_valid_submission_returns_ok(self):
        res = self.client.post(self.url, VALID_DATA)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])

    def test_valid_submission_creates_record(self):
        self.client.post(self.url, VALID_DATA)
        self.assertEqual(SponsorInquiry.objects.count(), 1)

    def test_all_fields_saved_correctly(self):
        self.client.post(self.url, VALID_DATA)
        s = SponsorInquiry.objects.get()
        self.assertEqual(s.company_name, 'Acme Corp')
        self.assertEqual(s.contact_name, 'Jane Smith')
        self.assertEqual(s.email, 'jane@acme.com')
        self.assertEqual(s.phone, '+1 555-123-4567')
        self.assertEqual(s.website, 'https://acme.com')
        self.assertEqual(s.budget, '5k_10k')
        self.assertTrue(s.interest_teams)
        self.assertTrue(s.goal_brand_awareness)
        self.assertTrue(s.activation_social)
        self.assertEqual(s.notes, 'Interested in jersey branding.')
        self.assertTrue(s.wants_proposal)

    def test_optional_fields_default_false(self):
        self.client.post(self.url, VALID_DATA)
        s = SponsorInquiry.objects.get()
        self.assertFalse(s.interest_players)
        self.assertFalse(s.interest_showcases)
        self.assertFalse(s.interest_tournaments)
        self.assertFalse(s.interest_full_program)
        self.assertFalse(s.goal_youth_athletes)
        self.assertFalse(s.goal_community)
        self.assertFalse(s.goal_marketing)
        self.assertFalse(s.goal_international)
        self.assertFalse(s.activation_logo)
        self.assertFalse(s.activation_event)
        self.assertFalse(s.activation_onsite)
        self.assertIsNone(s.logo.name or None)

    def test_str_representation(self):
        self.client.post(self.url, VALID_DATA)
        s = SponsorInquiry.objects.get()
        self.assertEqual(str(s), 'Acme Corp — Jane Smith')

    def test_minimal_required_fields_only(self):
        data = {
            'company_name': 'Min Corp',
            'contact_name': 'Bob',
            'email': 'bob@min.com',
            'phone': '5551234567',
        }
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])

    # ── GET not allowed ─────────────────────────────────────────────────

    def test_get_returns_405(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 405)

    # ── Missing required fields ─────────────────────────────────────────

    def test_missing_company_name_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'company_name': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('company_name', res.json()['errors'])

    def test_missing_contact_name_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'contact_name': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('contact_name', res.json()['errors'])

    def test_missing_email_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'email': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('email', res.json()['errors'])

    def test_invalid_email_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'email': 'not-an-email'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('email', res.json()['errors'])

    def test_missing_phone_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'phone': ''})
        self.assertEqual(res.status_code, 400)
        self.assertIn('phone', res.json()['errors'])

    def test_short_phone_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'phone': '123'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('phone', res.json()['errors'])

    def test_short_company_name_returns_error(self):
        res = self.client.post(self.url, {**VALID_DATA, 'company_name': 'A'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('company_name', res.json()['errors'])

    def test_no_record_saved_on_invalid_data(self):
        self.client.post(self.url, {**VALID_DATA, 'email': ''})
        self.assertEqual(SponsorInquiry.objects.count(), 0)

    # ── Response format ─────────────────────────────────────────────────

    def test_response_is_json(self):
        res = self.client.post(self.url, VALID_DATA)
        self.assertEqual(res['Content-Type'], 'application/json')

    def test_error_response_has_errors_key(self):
        res = self.client.post(self.url, {**VALID_DATA, 'email': ''})
        body = res.json()
        self.assertFalse(body['ok'])
        self.assertIn('errors', body)
