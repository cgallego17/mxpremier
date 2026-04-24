from django.db import models
from django.utils.translation import gettext_lazy as _
from jugadores.choices import AMERICAS_CHOICES


POSICIONES = [
    ('P', 'Pitcher'),
    ('C', 'Catcher'),
    ('1B', 'First Base'),
    ('2B', 'Second Base'),
    ('3B', 'Third Base'),
    ('SS', 'Shortstop'),
    ('LF', 'Left Field'),
    ('CF', 'Center Field'),
    ('RF', 'Right Field'),
    ('OF', 'Outfield'),
    ('DH', 'Designated Hitter'),
    ('UTIL', 'Utility'),
]


class Jugador(models.Model):
    # ── Player information ─────────���──────────────────────
    nombre = models.CharField(max_length=100, verbose_name=_('First name'))
    apellidos = models.CharField(max_length=100, verbose_name=_('Last names'))
    fecha_nacimiento = models.DateField(
        null=True, blank=True, verbose_name=_('Date of birth')
    )
    pais = models.CharField(
        max_length=3, choices=AMERICAS_CHOICES, blank=True, verbose_name=_('Country')
    )
    estado = models.CharField(
        max_length=100, blank=True, verbose_name=_('State / Province')
    )
    ciudad = models.CharField(
        max_length=100, blank=True, verbose_name=_('City')
    )
    nacionalidad = models.CharField(
        max_length=3, choices=AMERICAS_CHOICES, verbose_name=_('Nationality')
    )
    doble_nacionalidad = models.BooleanField(
        default=False, verbose_name=_('Dual nationality')
    )
    segunda_nacionalidad = models.CharField(
        max_length=3, choices=AMERICAS_CHOICES, blank=True, null=True,
        verbose_name=_('Second nationality'),
    )
    instagram = models.CharField(
        max_length=60, blank=True, verbose_name=_('Instagram handle')
    )

    # ── Additional player info ────────────────────────────
    equipo_viaje = models.CharField(
        max_length=150, blank=True, verbose_name=_('Travel team name')
    )
    equipo_ciudad_estado = models.CharField(
        max_length=150, blank=True, verbose_name=_('Team city and state')
    )
    posicion_principal = models.CharField(
        max_length=4, choices=POSICIONES, blank=True,
        verbose_name=_('Primary position')
    )
    posicion_secundaria = models.CharField(
        max_length=4, choices=POSICIONES, blank=True,
        verbose_name=_('Secondary position')
    )
    es_pitcher = models.BooleanField(default=False, verbose_name=_('Pitcher?'))

    # ── Parents / guardian ────────────────────────────────
    tutor_nombre = models.CharField(
        max_length=100, blank=True, verbose_name=_('Guardian first name')
    )
    tutor_apellidos = models.CharField(
        max_length=100, blank=True, verbose_name=_('Guardian last name')
    )
    tutor_telefono = models.CharField(
        max_length=20, blank=True, verbose_name=_('Guardian phone')
    )
    tutor_email = models.EmailField(blank=True, verbose_name=_('Guardian email'))

    # ── Legacy / meta ─────────────────────────────────────
    email = models.EmailField(
        unique=True, blank=True, verbose_name=_('Email')
    )
    telefono = models.CharField(
        max_length=20, blank=True, verbose_name=_('Phone')
    )
    edad = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name=_('Age')
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True, verbose_name=_('Registration date')
    )

    class Meta:
        verbose_name = _('Player')
        verbose_name_plural = _('Players')
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f'{self.apellidos}, {self.nombre}'
