from django.db import models
from django.utils.translation import gettext_lazy as _
from jugadores.choices import AMERICAS_CHOICES


class Pais(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    orden = models.PositiveSmallIntegerField(
        default=999,
        help_text='Lower number = shown first (baseball relevance)',
    )

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='estados')
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['nombre']
        unique_together = [('pais', 'codigo')]
        verbose_name = _('State / Province')
        verbose_name_plural = _('States / Provinces')

    def __str__(self):
        return self.nombre


class Ciudad(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='ciudades')
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ['nombre']
        unique_together = [('estado', 'nombre')]
        verbose_name = _('City')
        verbose_name_plural = _('Cities')

    def __str__(self):
        return self.nombre


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
    # ── Player information ───────────────────────────────
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
    equipo_pais = models.CharField(
        max_length=3, choices=AMERICAS_CHOICES, blank=True,
        verbose_name=_('Team country')
    )
    equipo_estado = models.CharField(
        max_length=100, blank=True, verbose_name=_('Team state')
    )
    equipo_ciudad = models.CharField(
        max_length=100, blank=True, verbose_name=_('Team city')
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

    def save(self, *args, **kwargs):
        import datetime
        if self.fecha_nacimiento:
            today = datetime.date.today()
            self.edad = today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        else:
            self.edad = None
        super().save(*args, **kwargs)
