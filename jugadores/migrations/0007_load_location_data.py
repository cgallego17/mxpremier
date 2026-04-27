"""
Data migration: populate Pais, Estado, Ciudad from the static location_data.py
"""
from django.db import migrations


def load_location_data(apps, schema_editor):
    from jugadores.location_data import LOCATION_DATA
    from jugadores.choices import AMERICAS_CHOICES

    Pais = apps.get_model('jugadores', 'Pais')
    Estado = apps.get_model('jugadores', 'Estado')
    Ciudad = apps.get_model('jugadores', 'Ciudad')

    # Build a name lookup from AMERICAS_CHOICES
    nombre_por_codigo = {codigo: str(nombre) for codigo, nombre in AMERICAS_CHOICES}

    for pais_codigo, data in LOCATION_DATA.items():
        nombre_pais = nombre_por_codigo.get(pais_codigo, pais_codigo)
        pais_obj, _ = Pais.objects.get_or_create(
            codigo=pais_codigo,
            defaults={'nombre': nombre_pais},
        )

        for estado_codigo, estado_nombre in data.get('states', []):
            estado_obj, _ = Estado.objects.get_or_create(
                pais=pais_obj,
                codigo=estado_codigo,
                defaults={'nombre': estado_nombre},
            )

        cities_map = data.get('cities', {})
        for estado_codigo, city_list in cities_map.items():
            try:
                estado_obj = Estado.objects.get(pais=pais_obj, codigo=estado_codigo)
            except Estado.DoesNotExist:
                continue
            for ciudad_nombre in city_list:
                Ciudad.objects.get_or_create(
                    estado=estado_obj,
                    nombre=ciudad_nombre,
                )


def reverse_load_location_data(apps, schema_editor):
    Pais = apps.get_model('jugadores', 'Pais')
    Pais.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('jugadores', '0006_pais_estado_ciudad'),
    ]

    operations = [
        migrations.RunPython(load_location_data, reverse_load_location_data),
    ]
