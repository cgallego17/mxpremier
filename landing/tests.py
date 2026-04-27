import datetime
from django.core.cache import cache
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from jugadores.models import Jugador  # pylint: disable=no-member


VALID_DATA = {
    'telefono': '555-0000',
    'nombre': 'John',
    'apellidos': 'Doe',
    'fecha_nacimiento': '2010-05-15',
    'pais': 'USA',
    'estado': 'CA',
    'ciudad': 'Los Angeles',
    'nacionalidad': 'USA',
    'equipo_viaje': 'LA Stars',
    'equipo_ciudad_estado': 'Los Angeles, CA',
    'posicion_principal': 'SS',
    'posicion_secundaria': 'OF',
    'tutor_nombre': 'Jane',
    'tutor_apellidos': 'Doe',
    'tutor_telefono': '555-1234',
    'tutor_email': 'jane@example.com',
}


class RegistroViewTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.url = reverse('landing:registro')
        cache.clear()

    # ── Happy path ──────────────────────────────────────────────────────

    def test_valid_submission_returns_ok(self):
        res = self.client.post(self.url, VALID_DATA)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])

    def test_valid_submission_creates_player(self):
        self.client.post(self.url, VALID_DATA)
        self.assertEqual(Jugador.objects.count(), 1)
        jugador = Jugador.objects.first()
        self.assertEqual(jugador.nombre, 'John')
        self.assertEqual(jugador.apellidos, 'Doe')
        self.assertEqual(jugador.pais, 'USA')
        self.assertEqual(jugador.estado, 'CA')
        self.assertEqual(jugador.ciudad, 'Los Angeles')

    def test_tutor_email_used_as_email_when_no_direct_email(self):
        self.client.post(self.url, VALID_DATA)
        jugador = Jugador.objects.first()
        self.assertEqual(jugador.email, 'jane@example.com')

    def test_optional_fields_not_required(self):
        data = {**VALID_DATA, 'instagram': '', 'es_pitcher': False}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])

    # ── GET not allowed ─────────────────────────────────────────────────

    def test_get_returns_405(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 405)

    # ── Missing required fields ─────────────────────────────────────────

    def test_missing_nombre_returns_error(self):
        data = {**VALID_DATA, 'nombre': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('nombre', res.json()['errors'])

    def test_missing_apellidos_returns_error(self):
        data = {**VALID_DATA, 'apellidos': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('apellidos', res.json()['errors'])

    def test_missing_fecha_nacimiento_returns_error(self):
        data = {**VALID_DATA, 'fecha_nacimiento': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('fecha_nacimiento', res.json()['errors'])

    def test_missing_pais_returns_error(self):
        data = {**VALID_DATA, 'pais': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('pais', res.json()['errors'])

    def test_missing_ciudad_returns_error(self):
        data = {**VALID_DATA, 'ciudad': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('ciudad', res.json()['errors'])

    def test_estado_is_optional(self):
        data = {**VALID_DATA, 'estado': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])

    def test_missing_nacionalidad_returns_error(self):
        data = {**VALID_DATA, 'nacionalidad': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('nacionalidad', res.json()['errors'])

    def test_missing_tutor_email_returns_error(self):
        data = {**VALID_DATA, 'tutor_email': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('tutor_email', res.json()['errors'])

    def test_invalid_tutor_email_format_returns_error(self):
        data = {**VALID_DATA, 'tutor_email': 'not-an-email'}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('tutor_email', res.json()['errors'])

    def test_no_player_saved_on_invalid_data(self):
        data = {**VALID_DATA, 'nombre': ''}
        self.client.post(self.url, data)
        self.assertEqual(Jugador.objects.count(), 0)

    # ── Dual nationality ────────────────────────────────────────────────

    def test_dual_nationality_without_second_returns_error(self):
        data = {**VALID_DATA, 'doble_nacionalidad': True, 'segunda_nacionalidad': ''}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 400)
        self.assertIn('segunda_nacionalidad', res.json()['errors'])

    def test_dual_nationality_with_second_is_valid(self):
        data = {**VALID_DATA, 'doble_nacionalidad': True, 'segunda_nacionalidad': 'MEX'}
        res = self.client.post(self.url, data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['ok'])
        jugador = Jugador.objects.first()
        self.assertEqual(jugador.segunda_nacionalidad, 'MEX')

    def test_no_dual_nationality_clears_second(self):
        data = {**VALID_DATA, 'doble_nacionalidad': False, 'segunda_nacionalidad': 'MEX'}
        self.client.post(self.url, data)
        jugador = Jugador.objects.first()
        self.assertIsNone(jugador.segunda_nacionalidad)

    # ── Response format ─────────────────────────────────────────────────

    def test_response_is_json(self):
        res = self.client.post(self.url, VALID_DATA)
        self.assertEqual(res['Content-Type'], 'application/json')

    def test_error_response_has_errors_key(self):
        data = {**VALID_DATA, 'nombre': ''}
        res = self.client.post(self.url, data)
        body = res.json()
        self.assertFalse(body['ok'])
        self.assertIn('errors', body)

    # ── Rate limiting ────────────────────────────────────────────────────

    @override_settings(REGISTRO_RATE_LIMIT=3)
    def test_rate_limit_blocks_after_limit(self):
        # Use different tutor emails to avoid unique constraint on each valid submit
        for i in range(3):
            data = {**VALID_DATA, 'tutor_email': f'user{i}@example.com'}
            res = self.client.post(self.url, data)
            self.assertNotEqual(res.status_code, 429, f'Request {i+1} should not be blocked')
        # 4th request should be rate limited
        res = self.client.post(self.url, {**VALID_DATA, 'tutor_email': 'user99@example.com'})
        self.assertEqual(res.status_code, 429)
        self.assertFalse(res.json()['ok'])
        self.assertEqual(res.json()['error'], 'too_many_requests')

    @override_settings(REGISTRO_RATE_LIMIT=3)
    def test_rate_limit_does_not_save_blocked_request(self):
        for i in range(3):
            data = {**VALID_DATA, 'tutor_email': f'user{i}@example.com'}
            self.client.post(self.url, data)
        count_before = Jugador.objects.count()
        self.client.post(self.url, {**VALID_DATA, 'tutor_email': 'user99@example.com'})
        self.assertEqual(Jugador.objects.count(), count_before)

    @override_settings(REGISTRO_RATE_LIMIT=3)
    def test_different_ips_have_separate_limits(self):
        # Fill up limit for 127.0.0.1
        for i in range(3):
            data = {**VALID_DATA, 'tutor_email': f'a{i}@example.com'}
            self.client.post(self.url, data, REMOTE_ADDR='127.0.0.1')
        # A different IP should still be allowed
        data = {**VALID_DATA, 'tutor_email': 'other@example.com'}
        res = self.client.post(self.url, data, REMOTE_ADDR='10.0.0.1')
        self.assertNotEqual(res.status_code, 429)

    # ── Save integrity ───────────────────────────────────────────────────

    def test_all_fields_saved_correctly(self):
        data = {
            **VALID_DATA,
            'doble_nacionalidad': True,
            'segunda_nacionalidad': 'MEX',
            'instagram': '@johndoe',
            'es_pitcher': True,
            'posicion_principal': 'P',
            'posicion_secundaria': 'SS',
        }
        self.client.post(self.url, data)
        j = Jugador.objects.get()
        self.assertEqual(j.nombre, 'John')
        self.assertEqual(j.apellidos, 'Doe')
        self.assertEqual(j.fecha_nacimiento, datetime.date(2010, 5, 15))
        self.assertEqual(j.pais, 'USA')
        self.assertEqual(j.estado, 'CA')
        self.assertEqual(j.ciudad, 'Los Angeles')
        self.assertEqual(j.nacionalidad, 'USA')
        self.assertTrue(j.doble_nacionalidad)
        self.assertEqual(j.segunda_nacionalidad, 'MEX')
        self.assertEqual(j.instagram, '@johndoe')
        self.assertTrue(j.es_pitcher)
        self.assertEqual(j.equipo_viaje, 'LA Stars')
        self.assertEqual(j.equipo_ciudad_estado, 'Los Angeles, CA')
        self.assertEqual(j.posicion_principal, 'P')
        self.assertEqual(j.posicion_secundaria, 'SS')
        self.assertEqual(j.tutor_nombre, 'Jane')
        self.assertEqual(j.tutor_apellidos, 'Doe')
        self.assertEqual(j.tutor_telefono, '555-1234')
        self.assertEqual(j.tutor_email, 'jane@example.com')
        self.assertEqual(j.email, 'jane@example.com')

    def test_optional_fields_default_correctly(self):
        self.client.post(self.url, VALID_DATA)
        j = Jugador.objects.get()
        self.assertEqual(j.instagram, '')
        self.assertFalse(j.doble_nacionalidad)
        self.assertIsNone(j.segunda_nacionalidad)
        self.assertFalse(j.es_pitcher)
        self.assertEqual(j.estado, 'CA')

    def test_str_representation(self):
        self.client.post(self.url, VALID_DATA)
        j = Jugador.objects.get()
        self.assertEqual(str(j), 'Doe, John')

    def test_duplicate_email_rejected(self):
        self.client.post(self.url, VALID_DATA)
        res = self.client.post(self.url, {**VALID_DATA, 'nombre': 'Jane'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('tutor_email', res.json()['errors'])
        self.assertEqual(Jugador.objects.count(), 1)

    # ── Backend field validation ─────────────────────────────────────────

    def test_nombre_too_short_rejected(self):
        res = self.client.post(self.url, {**VALID_DATA, 'nombre': 'J'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('nombre', res.json()['errors'])

    def test_apellidos_too_short_rejected(self):
        res = self.client.post(self.url, {**VALID_DATA, 'apellidos': 'D'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('apellidos', res.json()['errors'])

    def test_future_birth_date_rejected(self):
        future = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        res = self.client.post(self.url, {**VALID_DATA, 'fecha_nacimiento': future})
        self.assertEqual(res.status_code, 400)
        self.assertIn('fecha_nacimiento', res.json()['errors'])


    def test_telefono_y_edad_se_guardan_correctamente(self):
        data = {
            **VALID_DATA,
            'telefono': '1234567890',
            'fecha_nacimiento': '2010-05-15',
        }
        self.client.post(self.url, data)
        jugador = Jugador.objects.first()
        self.assertEqual(jugador.telefono, '1234567890')
        # Edad calculada
        hoy = datetime.date.today()
        nacimiento = datetime.date(2010, 5, 15)
        edad_esperada = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        self.assertEqual(jugador.edad, edad_esperada)
