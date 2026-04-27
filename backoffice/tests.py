from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, timedelta
from backoffice.forms import JugadorForm
from jugadores.models import Jugador


VALID_FORM_DATA = {
    'nombre': 'Juan',
    'apellidos': 'Pérez García',
    'fecha_nacimiento': date(2010, 5, 15),
    'pais': 'MEX',
    'estado': 'DIF',
    'ciudad': 'Ciudad de Mexico',
    'nacionalidad': 'MEX',
    'doble_nacionalidad': False,
    'equipo_viaje': 'Tigres',
    'equipo_pais': 'MEX',
    'equipo_estado': 'NLE',
    'equipo_ciudad': 'Monterrey',
    'posicion_principal': 'SS',
    'posicion_secundaria': '2B',
    'es_pitcher': False,
    'telefono': '',
    'tutor_nombre': 'María',
    'tutor_apellidos': 'López',
    'tutor_telefono': '5281123456',
    'tutor_email': 'maria.lopez@example.com',
}


class JugadorFormTest(TestCase):

    def setUp(self):
        self.valid_data = dict(VALID_FORM_DATA)

    # ── Required field validation ────────────────────────────────────────

    def test_form_valido(self):
        form = JugadorForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_nombre_requerido(self):
        data = {**self.valid_data, 'nombre': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_nombre_minimo_2_caracteres(self):
        data = {**self.valid_data, 'nombre': 'J'}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_apellidos_requerido(self):
        data = {**self.valid_data, 'apellidos': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('apellidos', form.errors)

    def test_apellidos_minimo_2_caracteres(self):
        data = {**self.valid_data, 'apellidos': 'P'}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('apellidos', form.errors)

    def test_fecha_nacimiento_futuro_invalida(self):
        data = {**self.valid_data, 'fecha_nacimiento': date.today() + timedelta(days=30)}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_nacimiento', form.errors)

    def test_pais_requerido(self):
        data = {**self.valid_data, 'pais': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('pais', form.errors)

    def test_nacionalidad_requerida(self):
        data = {**self.valid_data, 'nacionalidad': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('nacionalidad', form.errors)

    def test_equipo_viaje_requerido(self):
        data = {**self.valid_data, 'equipo_viaje': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('equipo_viaje', form.errors)

    def test_posicion_principal_requerida(self):
        data = {**self.valid_data, 'posicion_principal': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('posicion_principal', form.errors)

    def test_posicion_secundaria_requerida(self):
        data = {**self.valid_data, 'posicion_secundaria': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('posicion_secundaria', form.errors)

    def test_tutor_nombre_requerido(self):
        data = {**self.valid_data, 'tutor_nombre': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor_nombre', form.errors)

    def test_tutor_apellidos_requerido(self):
        data = {**self.valid_data, 'tutor_apellidos': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor_apellidos', form.errors)

    def test_tutor_telefono_requerido(self):
        data = {**self.valid_data, 'tutor_telefono': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor_telefono', form.errors)

    def test_tutor_email_requerido(self):
        data = {**self.valid_data, 'tutor_email': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('tutor_email', form.errors)

    # ── Optional fields ──────────────────────────────────────────────────

    def test_campos_opcionales_no_requeridos(self):
        data = {**self.valid_data, 'instagram': '', 'estado': '', 'ciudad': '', 'es_pitcher': False}
        form = JugadorForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_equipo_pais_opcional(self):
        data = {**self.valid_data, 'equipo_pais': '', 'equipo_estado': '', 'equipo_ciudad': ''}
        form = JugadorForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    # ── Dual nationality ─────────────────────────────────────────────────

    def test_doble_nacionalidad_requiere_segunda(self):
        data = {**self.valid_data, 'doble_nacionalidad': True, 'segunda_nacionalidad': ''}
        form = JugadorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('segunda_nacionalidad', form.errors)

    def test_doble_nacionalidad_con_segunda_valida(self):
        data = {**self.valid_data, 'doble_nacionalidad': True, 'segunda_nacionalidad': 'USA'}
        form = JugadorForm(data=data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    # ── Duplicate email ──────────────────────────────────────────────────

    def test_duplicate_tutor_email_rejected(self):
        form1 = JugadorForm(data=self.valid_data)
        self.assertTrue(form1.is_valid())
        form1.save()
        data2 = {**self.valid_data, 'nombre': 'Pedro', 'apellidos': 'Ramirez'}
        form2 = JugadorForm(data=data2)
        self.assertFalse(form2.is_valid())
        self.assertIn('tutor_email', form2.errors)

    # ── Save integrity ───────────────────────────────────────────────────

    def test_creacion_exitosa_jugador(self):
        form = JugadorForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        jugador = form.save()
        self.assertEqual(jugador.nombre, 'Juan')
        self.assertEqual(jugador.apellidos, 'Pérez García')
        self.assertEqual(jugador.pais, 'MEX')
        self.assertEqual(jugador.estado, 'DIF')
        self.assertEqual(jugador.ciudad, 'Ciudad de Mexico')
        self.assertEqual(jugador.equipo_pais, 'MEX')
        self.assertEqual(jugador.equipo_estado, 'NLE')
        self.assertEqual(jugador.equipo_ciudad, 'Monterrey')
        self.assertEqual(jugador.posicion_principal, 'SS')
        self.assertEqual(jugador.tutor_email, 'maria.lopez@example.com')
        self.assertIsNotNone(jugador.edad)

    def test_edad_calculada_automaticamente(self):
        form = JugadorForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        jugador = form.save()
        today = date.today()
        dob = date(2010, 5, 15)
        expected_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        self.assertEqual(jugador.edad, expected_age)


class BackofficeJugadorViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')
        self.client.login(username='admin', password='password')
        self.lista_url = reverse('backoffice:jugadores_lista')
        self.crear_url = reverse('backoffice:jugador_crear')

    def test_lista_requires_login(self):
        self.client.logout()
        res = self.client.get(self.lista_url)
        self.assertNotEqual(res.status_code, 200)

    def test_lista_visible_for_staff(self):
        res = self.client.get(self.lista_url)
        self.assertEqual(res.status_code, 200)

    def test_crear_get_returns_200(self):
        res = self.client.get(self.crear_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'location_data_json' if False else 'id_pais')

    def test_crear_post_valid_creates_player(self):
        data = dict(VALID_FORM_DATA)
        data['fecha_nacimiento'] = '2010-05-15'
        res = self.client.post(self.crear_url, data)
        self.assertEqual(Jugador.objects.count(), 1)
        self.assertRedirects(res, self.lista_url)

    def test_crear_post_invalid_shows_errors(self):
        data = dict(VALID_FORM_DATA)
        data['fecha_nacimiento'] = '2010-05-15'
        data['nombre'] = ''
        res = self.client.post(self.crear_url, data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Jugador.objects.count(), 0)

    def test_editar_preloads_values(self):
        j = Jugador.objects.create(
            nombre='Ana', apellidos='Cruz', fecha_nacimiento=date(2012, 3, 1),
            pais='USA', estado='CA', ciudad='Los Angeles',
            nacionalidad='USA', equipo_viaje='LA Stars',
            equipo_pais='USA', equipo_estado='CA', equipo_ciudad='Los Angeles',
            posicion_principal='C', posicion_secundaria='OF',
            tutor_nombre='Bob', tutor_apellidos='Cruz',
            tutor_telefono='555-9999', tutor_email='bob@test.com',
        )
        res = self.client.get(reverse('backoffice:jugador_editar', args=[j.pk]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Ana')

    def test_lista_shows_location_fields(self):
        Jugador.objects.create(
            nombre='Test', apellidos='Player', fecha_nacimiento=date(2011, 1, 1),
            pais='MEX', estado='NLE', ciudad='Monterrey',
            nacionalidad='MEX', equipo_viaje='Tigers',
            equipo_pais='MEX', equipo_estado='NLE', equipo_ciudad='Monterrey',
            posicion_principal='P', posicion_secundaria='SS',
            tutor_nombre='Papa', tutor_apellidos='Player',
            tutor_telefono='555-0001', tutor_email='papa@test.com',
        )
        res = self.client.get(self.lista_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Monterrey')
        self.assertContains(res, 'NLE')


