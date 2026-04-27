from django.test import TestCase, Client
from django.urls import reverse
from jugadores.models import Pais, Estado, Ciudad
import json


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Helpers â€” use TEST-prefixed codes that never clash with migrated real data
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def create_pais(codigo='T_MEX', nombre='Test Mexico', orden=6):
    return Pais.objects.create(codigo=codigo, nombre=nombre, orden=orden)


def create_estado(pais, codigo='T_JAL', nombre='Test Jalisco'):
    return Estado.objects.create(pais=pais, codigo=codigo, nombre=nombre)


def create_ciudad(estado, nombre='Test Guadalajara'):
    return Ciudad.objects.create(estado=estado, nombre=nombre)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Model tests
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class PaisModelTest(TestCase):

    def test_str(self):
        p = create_pais()
        self.assertEqual(str(p), 'Test Mexico')

    def test_baseball_priority_ordering(self):
        """Countries with lower orden value must appear first (among test entries)."""
        Pais.objects.all().delete()   # clear migrated data for isolated ordering test
        Pais.objects.create(codigo='T_DOM', nombre='Test DR',  orden=1)
        Pais.objects.create(codigo='T_VEN', nombre='Test VEN', orden=2)
        Pais.objects.create(codigo='T_CUB', nombre='Test CUB', orden=3)
        Pais.objects.create(codigo='T_USA', nombre='Test USA', orden=5)
        Pais.objects.create(codigo='T_ZZZ', nombre='Zzz',     orden=999)

        ordered = list(Pais.objects.values_list('codigo', flat=True))
        self.assertEqual(ordered[0], 'T_DOM')
        self.assertEqual(ordered[1], 'T_VEN')
        self.assertEqual(ordered[2], 'T_CUB')
        self.assertEqual(ordered[3], 'T_USA')
        self.assertEqual(ordered[4], 'T_ZZZ')

    def test_default_orden_is_999(self):
        p = Pais.objects.create(codigo='T_XYZ', nombre='Unknown')
        self.assertEqual(p.orden, 999)

    def test_codigo_unique(self):
        create_pais()
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Pais.objects.create(codigo='T_MEX', nombre='Duplicate')


class EstadoModelTest(TestCase):

    def setUp(self):
        self.mex = create_pais()

    def test_str(self):
        e = create_estado(self.mex)
        self.assertEqual(str(e), 'Test Jalisco')

    def test_estado_belongs_to_pais(self):
        e = create_estado(self.mex)
        self.assertEqual(e.pais, self.mex)

    def test_codigo_unique_per_pais(self):
        create_estado(self.mex, codigo='T_JAL')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Estado.objects.create(pais=self.mex, codigo='T_JAL', nombre='Duplicate')

    def test_same_codigo_different_pais_allowed(self):
        usa = create_pais('T_USA', 'Test USA', orden=5)
        create_estado(self.mex, codigo='T_CA', nombre='Test Campeche')
        create_estado(usa,      codigo='T_CA', nombre='Test California')
        self.assertEqual(Estado.objects.filter(codigo='T_CA').count(), 2)

    def test_delete_pais_cascades_to_estados(self):
        create_estado(self.mex)
        self.mex.delete()
        self.assertEqual(Estado.objects.filter(codigo='T_JAL').count(), 0)


class CiudadModelTest(TestCase):

    def setUp(self):
        self.mex = create_pais()
        self.jal = create_estado(self.mex)

    def test_str(self):
        c = create_ciudad(self.jal)
        self.assertEqual(str(c), 'Test Guadalajara')

    def test_ciudad_belongs_to_estado(self):
        c = create_ciudad(self.jal)
        self.assertEqual(c.estado, self.jal)

    def test_nombre_unique_per_estado(self):
        create_ciudad(self.jal, 'Test City A')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Ciudad.objects.create(estado=self.jal, nombre='Test City A')

    def test_same_nombre_different_estado_allowed(self):
        nle = create_estado(self.mex, codigo='T_NLE', nombre='Test NL')
        create_ciudad(self.jal, 'Test Monterrey')
        create_ciudad(nle,      'Test Monterrey')
        self.assertEqual(Ciudad.objects.filter(nombre='Test Monterrey').count(), 2)

    def test_delete_estado_cascades_to_ciudades(self):
        create_ciudad(self.jal)
        self.jal.delete()
        self.assertEqual(Ciudad.objects.filter(nombre='Test Guadalajara').count(), 0)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# API endpoint tests (isolated with test codes)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class PaisesAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        # Use codes guaranteed not in the comprehensive data
        self.p1 = Pais.objects.create(codigo='TA1', nombre='Test Alpha',  orden=1)
        self.p2 = Pais.objects.create(codigo='TA2', nombre='Test Beta',   orden=2)
        self.p3 = Pais.objects.create(codigo='TA3', nombre='Test Gamma',  orden=6)
        self.p4 = Pais.objects.create(codigo='TA4', nombre='Zzz Last',    orden=999)

    def test_paises_returns_200(self):
        res = self.client.get('/api/locations/paises/')
        self.assertEqual(res.status_code, 200)

    def test_paises_content_type_json(self):
        res = self.client.get('/api/locations/paises/')
        self.assertEqual(res['Content-Type'], 'application/json')

    def test_paises_test_entries_present(self):
        res = self.client.get('/api/locations/paises/')
        data = json.loads(res.content)
        codigos = [p['codigo'] for p in data['paises']]
        self.assertIn('TA1', codigos)
        self.assertIn('TA4', codigos)

    def test_paises_test_entries_baseball_order(self):
        """TA1 (orden=1) must appear before TA4 (orden=999)."""
        res = self.client.get('/api/locations/paises/')
        data = json.loads(res.content)
        codigos = [p['codigo'] for p in data['paises']]
        self.assertLess(codigos.index('TA1'), codigos.index('TA2'))
        self.assertLess(codigos.index('TA2'), codigos.index('TA3'))
        self.assertLess(codigos.index('TA3'), codigos.index('TA4'))

    def test_paises_includes_required_fields(self):
        res = self.client.get('/api/locations/paises/')
        data = json.loads(res.content)
        # find one of our test entries
        pais = next(p for p in data['paises'] if p['codigo'] == 'TA1')
        self.assertIn('codigo', pais)
        self.assertIn('nombre', pais)
        self.assertIn('orden', pais)


class EstadosAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.mex = Pais.objects.create(codigo='TB_MEX', nombre='Test Mexico', orden=6)
        self.jal = Estado.objects.create(pais=self.mex, codigo='TB_JAL', nombre='Test Jalisco')
        self.nle = Estado.objects.create(pais=self.mex, codigo='TB_NLE', nombre='Test Nuevo Leon')
        self.dif = Estado.objects.create(pais=self.mex, codigo='TB_DIF', nombre='Test CDMX')
        self.usa = Pais.objects.create(codigo='TB_USA', nombre='Test USA', orden=5)
        self.ca  = Estado.objects.create(pais=self.usa, codigo='TB_CA',  nombre='Test California')

    def test_estados_returns_200(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_MEX'})
        self.assertEqual(res.status_code, 200)

    def test_estados_for_mex_returns_3(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_MEX'})
        data = json.loads(res.content)
        self.assertEqual(len(data['estados']), 3)

    def test_estados_are_alphabetical(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_MEX'})
        data = json.loads(res.content)
        nombres = [e['nombre'] for e in data['estados']]
        self.assertEqual(nombres, sorted(nombres))

    def test_estados_for_usa_returns_1(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_USA'})
        data = json.loads(res.content)
        self.assertEqual(len(data['estados']), 1)
        self.assertEqual(data['estados'][0]['codigo'], 'TB_CA')

    def test_estados_no_pais_returns_empty(self):
        res = self.client.get('/api/locations/estados/')
        data = json.loads(res.content)
        self.assertEqual(data['estados'], [])

    def test_estados_unknown_pais_returns_empty(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'XXXYYY'})
        data = json.loads(res.content)
        self.assertEqual(data['estados'], [])

    def test_estados_includes_codigo_and_nombre(self):
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_MEX'})
        data = json.loads(res.content)
        estado = data['estados'][0]
        self.assertIn('codigo', estado)
        self.assertIn('nombre', estado)

    def test_estados_not_cross_contaminated(self):
        """MEX test estados must not include USA test estados."""
        res = self.client.get('/api/locations/estados/', {'pais': 'TB_MEX'})
        data = json.loads(res.content)
        codigos = [e['codigo'] for e in data['estados']]
        self.assertNotIn('TB_CA', codigos)


class CiudadesAPITest(TestCase):

    def setUp(self):
        self.client = Client()
        self.mex = Pais.objects.create(codigo='TC_MEX', nombre='Test Mexico', orden=6)
        self.jal = Estado.objects.create(pais=self.mex, codigo='TC_JAL', nombre='Test Jalisco')
        Ciudad.objects.create(estado=self.jal, nombre='TC Guadalajara')
        Ciudad.objects.create(estado=self.jal, nombre='TC Zapopan')
        Ciudad.objects.create(estado=self.jal, nombre='TC Tlaquepaque')
        self.nle = Estado.objects.create(pais=self.mex, codigo='TC_NLE', nombre='Test Nuevo Leon')
        Ciudad.objects.create(estado=self.nle, nombre='TC Monterrey')

    def test_ciudades_returns_200(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'TC_JAL'})
        self.assertEqual(res.status_code, 200)

    def test_ciudades_for_jal_returns_3(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertEqual(len(data['ciudades']), 3)

    def test_ciudades_are_alphabetical(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertEqual(data['ciudades'], sorted(data['ciudades']))

    def test_ciudades_correct_names(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertIn('TC Guadalajara', data['ciudades'])
        self.assertIn('TC Zapopan', data['ciudades'])

    def test_ciudades_no_pais_returns_empty(self):
        res = self.client.get('/api/locations/ciudades/', {'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertEqual(data['ciudades'], [])

    def test_ciudades_no_estado_returns_empty(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX'})
        data = json.loads(res.content)
        self.assertEqual(data['ciudades'], [])

    def test_ciudades_unknown_returns_empty(self):
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'XXXYYY'})
        data = json.loads(res.content)
        self.assertEqual(data['ciudades'], [])

    def test_ciudades_not_cross_contaminated(self):
        """JAL cities must not include NLE cities."""
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_MEX', 'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertNotIn('TC Monterrey', data['ciudades'])

    def test_ciudades_wrong_pais_for_estado_returns_empty(self):
        """TC_JAL belongs to TC_MEX, not TC_USA â€” should return empty."""
        Pais.objects.create(codigo='TC_USA', nombre='Test USA', orden=5)
        res = self.client.get('/api/locations/ciudades/', {'pais': 'TC_USA', 'estado': 'TC_JAL'})
        data = json.loads(res.content)
        self.assertEqual(data['ciudades'], [])


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Integration test: full cascade chain
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class CascadeIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        # Build full hierarchy with test-prefixed codes
        self.dom = Pais.objects.create(codigo='TI_DOM', nombre='Test DR',  orden=1)
        self.sn  = Estado.objects.create(pais=self.dom, codigo='TI_SN', nombre='Test Santiago')
        Ciudad.objects.create(estado=self.sn, nombre='TI Santiago City')
        Ciudad.objects.create(estado=self.sn, nombre='TI Villa Bisono')

        self.mex = Pais.objects.create(codigo='TI_MEX', nombre='Test Mexico', orden=6)
        self.nle = Estado.objects.create(pais=self.mex, codigo='TI_NLE', nombre='Test Nuevo Leon')
        Ciudad.objects.create(estado=self.nle, nombre='TI Monterrey')

    def test_full_cascade_dom(self):
        """Step 1: get countries â†’ Step 2: get states â†’ Step 3: get cities."""
        r1 = self.client.get('/api/locations/paises/')
        d1 = json.loads(r1.content)
        codigos = [p['codigo'] for p in d1['paises']]
        self.assertIn('TI_DOM', codigos)
        self.assertIn('TI_MEX', codigos)
        # TI_DOM (orden=1) must appear before TI_MEX (orden=6)
        self.assertLess(codigos.index('TI_DOM'), codigos.index('TI_MEX'))

        r2 = self.client.get('/api/locations/estados/', {'pais': 'TI_DOM'})
        d2 = json.loads(r2.content)
        self.assertEqual(len(d2['estados']), 1)
        self.assertEqual(d2['estados'][0]['codigo'], 'TI_SN')

        r3 = self.client.get('/api/locations/ciudades/', {'pais': 'TI_DOM', 'estado': 'TI_SN'})
        d3 = json.loads(r3.content)
        self.assertIn('TI Santiago City', d3['ciudades'])
        self.assertIn('TI Villa Bisono', d3['ciudades'])

    def test_full_cascade_mex(self):
        r1 = self.client.get('/api/locations/estados/', {'pais': 'TI_MEX'})
        d1 = json.loads(r1.content)
        self.assertEqual(d1['estados'][0]['codigo'], 'TI_NLE')

        r2 = self.client.get('/api/locations/ciudades/', {'pais': 'TI_MEX', 'estado': 'TI_NLE'})
        d2 = json.loads(r2.content)
        self.assertEqual(d2['ciudades'], ['TI Monterrey'])

    def test_no_leakage_between_countries(self):
        """States and cities from MEX must not appear when querying DOM."""
        r = self.client.get('/api/locations/estados/', {'pais': 'TI_DOM'})
        d = json.loads(r.content)
        codigos = [e['codigo'] for e in d['estados']]
        self.assertNotIn('TI_NLE', codigos)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Live DB data tests (validate real migrated data)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class LiveDataTest(TestCase):

    def test_total_paises_at_least_50(self):
        self.assertGreaterEqual(Pais.objects.count(), 50)

    def test_total_estados_at_least_500(self):
        self.assertGreaterEqual(Estado.objects.count(), 500)

    def test_total_ciudades_at_least_10000(self):
        self.assertGreaterEqual(Ciudad.objects.count(), 10000)

    def test_dom_is_first_baseball_country(self):
        first = Pais.objects.first()
        self.assertEqual(first.codigo, 'DOM')

    def test_mex_has_32_estados(self):
        mex = Pais.objects.get(codigo='MEX')
        self.assertEqual(Estado.objects.filter(pais=mex).count(), 32)

    def test_usa_has_at_least_50_estados(self):
        usa = Pais.objects.get(codigo='USA')
        self.assertGreaterEqual(Estado.objects.filter(pais=usa).count(), 50)

    def test_dom_has_estados(self):
        dom = Pais.objects.get(codigo='DOM')
        self.assertGreater(Estado.objects.filter(pais=dom).count(), 0)

    def test_mex_nle_has_cities(self):
        mex = Pais.objects.get(codigo='MEX')
        nle = Estado.objects.get(pais=mex, codigo='NLE')
        self.assertGreater(Ciudad.objects.filter(estado=nle).count(), 0)

    def test_usa_ca_has_cities(self):
        usa = Pais.objects.get(codigo='USA')
        ca = Estado.objects.get(pais=usa, codigo='CA')
        self.assertGreater(Ciudad.objects.filter(estado=ca).count(), 0)

    def test_baseball_priority_countries_in_top_10(self):
        top10 = list(Pais.objects.values_list('codigo', flat=True)[:10])
        for codigo in ['DOM', 'VEN', 'CUB', 'PRI', 'USA', 'MEX', 'PAN']:
            self.assertIn(codigo, top10, msg=f'{codigo} should be in top 10 baseball countries')

    def test_api_paises_dom_is_first(self):
        client = Client()
        res = client.get('/api/locations/paises/')
        data = json.loads(res.content)
        self.assertEqual(data['paises'][0]['codigo'], 'DOM',
                         'Dominican Republic must be first (highest baseball relevance)')

    def test_api_paises_top7_are_baseball_powers(self):
        client = Client()
        res = client.get('/api/locations/paises/')
        data = json.loads(res.content)
        top7 = [p['codigo'] for p in data['paises'][:7]]
        for codigo in ['DOM', 'VEN', 'CUB', 'PRI', 'USA', 'MEX', 'PAN']:
            self.assertIn(codigo, top7)

    def test_api_estados_mex_returns_32(self):
        client = Client()
        res = client.get('/api/locations/estados/', {'pais': 'MEX'})
        data = json.loads(res.content)
        self.assertEqual(len(data['estados']), 32)

    def test_api_estados_dom_returns_results(self):
        client = Client()
        res = client.get('/api/locations/estados/', {'pais': 'DOM'})
        data = json.loads(res.content)
        self.assertGreater(len(data['estados']), 0)

    def test_api_ciudades_mex_nle_returns_results(self):
        client = Client()
        res = client.get('/api/locations/ciudades/', {'pais': 'MEX', 'estado': 'NLE'})
        data = json.loads(res.content)
        self.assertGreater(len(data['ciudades']), 0)

    def test_api_ciudades_usa_ca_returns_results(self):
        client = Client()
        res = client.get('/api/locations/ciudades/', {'pais': 'USA', 'estado': 'CA'})
        data = json.loads(res.content)
        self.assertGreater(len(data['ciudades']), 0)

    def test_api_ciudades_ven_dc_returns_results(self):
        client = Client()
        res = client.get('/api/locations/estados/', {'pais': 'VEN'})
        data = json.loads(res.content)
        self.assertGreater(len(data['estados']), 0)

