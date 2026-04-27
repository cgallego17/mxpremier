"""
Data migration: reload Pais/Estado/Ciudad from the comprehensive
jugadores/fixtures/americas_locations.json (sourced from countries+states+cities.json,
Americas region only). Replaces the previous load from location_data.py.
Uses bulk_create for performance (43,000+ cities).
"""
import json
import os
from django.db import migrations


def reload_from_fixture(apps, schema_editor):
    Pais = apps.get_model('jugadores', 'Pais')
    Estado = apps.get_model('jugadores', 'Estado')
    Ciudad = apps.get_model('jugadores', 'Ciudad')

    # Clear old data
    Ciudad.objects.all().delete()
    Estado.objects.all().delete()
    Pais.objects.all().delete()

    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),  # jugadores/
        'fixtures',
        'americas_locations.json',
    )

    with open(fixture_path, encoding='utf-8-sig') as f:
        countries = json.load(f)

    for country_data in countries:
        pais_obj = Pais.objects.create(
            codigo=country_data['iso3'],
            nombre=country_data['name'],
        )

        estados_to_create = []
        states_with_cities = []
        for state_data in country_data.get('states', []):
            estados_to_create.append(
                Estado(pais=pais_obj, codigo=state_data['iso2'], nombre=state_data['name'])
            )
            states_with_cities.append((state_data['iso2'], state_data.get('cities', [])))

        # Bulk create all states for this country at once
        Estado.objects.bulk_create(estados_to_create, ignore_conflicts=True)

        # Reload states to get their PKs
        estado_map = {e.codigo: e for e in Estado.objects.filter(pais=pais_obj)}

        # Bulk create all cities
        ciudades_to_create = []
        seen = set()
        for estado_codigo, city_list in states_with_cities:
            estado_obj = estado_map.get(estado_codigo)
            if not estado_obj:
                continue
            for city_name in city_list:
                name = city_name.strip() if city_name else ''
                if not name:
                    continue
                key = (estado_obj.pk, name)
                if key in seen:
                    continue
                seen.add(key)
                ciudades_to_create.append(Ciudad(estado=estado_obj, nombre=name))

        Ciudad.objects.bulk_create(ciudades_to_create, batch_size=500, ignore_conflicts=True)


def reverse_reload(apps, schema_editor):
    Pais = apps.get_model('jugadores', 'Pais')
    Pais.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('jugadores', '0007_load_location_data'),
    ]

    operations = [
        migrations.RunPython(reload_from_fixture, reverse_reload),
    ]
