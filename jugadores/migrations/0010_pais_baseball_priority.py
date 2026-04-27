"""
Data migration: assign baseball relevance ordering to Pais records.
Countries with more MLB/international baseball presence get lower order numbers
and therefore appear first in dropdowns.
"""
from django.db import migrations

# Baseball priority order for Americas countries.
# Lower number = shown first. Based on MLB player pipeline representation.
BASEBALL_PRIORITY = {
    # ── Elite / MLB powerhouses ────────────────────────
    'DOM': 1,   # Dominican Republic – most MLB players per capita
    'VEN': 2,   # Venezuela – 2nd most MLB players
    'CUB': 3,   # Cuba – historic baseball powerhouse
    'PRI': 4,   # Puerto Rico – strong MLB tradition
    'USA': 5,   # United States – home of MLB
    'MEX': 6,   # Mexico – LMB + many MLB players
    'PAN': 7,   # Panama – Mariano Rivera, Rod Carew, etc.
    'NIC': 8,   # Nicaragua – growing pipeline
    # ── Strong presence ────────────────────────────────
    'COL': 9,
    'HND': 10,
    'CRI': 11,
    'GTM': 12,
    'SLV': 13,
    'CAN': 14,
    'BRA': 15,
    'ARG': 16,
    # ── Caribbean / rest ───────────────────────────────
    'JAM': 17,
    'TTO': 18,
    'CUR': 19,
    'CUW': 19,
    'BAH': 20,
    'BHS': 20,
    'BRB': 21,
    'GUY': 22,
    'HTI': 23,
    'ECU': 24,
    'PER': 25,
    'BOL': 26,
    'CHL': 27,
    'URY': 28,
    'PRY': 29,
    # All others default to 999 via model field default
}


def set_baseball_priority(apps, schema_editor):
    Pais = apps.get_model('jugadores', 'Pais')
    for codigo, orden in BASEBALL_PRIORITY.items():
        Pais.objects.filter(codigo=codigo).update(orden=orden)


def reverse_priority(apps, schema_editor):
    Pais = apps.get_model('jugadores', 'Pais')
    Pais.objects.all().update(orden=999)


class Migration(migrations.Migration):

    dependencies = [
        ('jugadores', '0009_pais_orden'),
    ]

    operations = [
        migrations.RunPython(set_baseball_priority, reverse_priority),
    ]
