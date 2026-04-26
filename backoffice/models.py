from django.db import models
from django.utils.translation import gettext_lazy as _


# ── Gastos ────────────────────────────────────────────────────────

CATEGORIAS_GASTO = [
    ('viaje',         _('Travel')),
    ('hospedaje',     _('Lodging')),
    ('uniformes',     _('Uniforms')),
    ('equipo',        _('Equipment')),
    ('alimentacion',  _('Food & Meals')),
    ('marketing',     _('Marketing')),
    ('sede',          _('Venue')),
    ('personal',      _('Personnel')),
    ('administrativo', _('Administrative')),
    ('otro',          _('Other')),
]

CATEGORIA_ICONS = {
    'viaje':         'bi-airplane',
    'hospedaje':     'bi-house',
    'uniformes':     'bi-person-badge',
    'equipo':        'bi-gear',
    'alimentacion':  'bi-egg-fried',
    'marketing':     'bi-megaphone',
    'sede':          'bi-building',
    'personal':      'bi-people',
    'administrativo': 'bi-file-earmark-text',
    'otro':          'bi-three-dots',
}

CATEGORIA_COLORS = {
    'viaje':         '#1A6B35',
    'hospedaje':     '#0D3B1E',
    'uniformes':     '#C41230',
    'equipo':        '#C8A830',
    'alimentacion':  '#2563EB',
    'marketing':     '#7C3AED',
    'sede':          '#0891B2',
    'personal':      '#059669',
    'administrativo': '#6B7280',
    'otro':          '#374151',
}

ESTADOS_GASTO = [
    ('pendiente',  _('Pending')),
    ('pagado',     _('Paid')),
    ('cancelado',  _('Cancelled')),
]

METODOS_PAGO = [
    ('efectivo',      _('Cash')),
    ('tarjeta',       _('Card')),
    ('transferencia', _('Transfer')),
    ('otro',          _('Other')),
]

MONEDAS = [
    ('USD', 'USD'),
    ('MXN', 'MXN'),
]


class Gasto(models.Model):
    titulo      = models.CharField(max_length=200, verbose_name=_('Title'))
    categoria   = models.CharField(
        max_length=20, choices=CATEGORIAS_GASTO,
        default='otro', verbose_name=_('Category')
    )
    monto       = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_('Amount')
    )
    moneda      = models.CharField(
        max_length=3, choices=MONEDAS, default='USD', verbose_name=_('Currency')
    )
    fecha       = models.DateField(verbose_name=_('Date'))
    metodo_pago = models.CharField(
        max_length=20, choices=METODOS_PAGO, blank=True,
        verbose_name=_('Payment method')
    )
    estado      = models.CharField(
        max_length=20, choices=ESTADOS_GASTO,
        default='pendiente', verbose_name=_('Status')
    )
    comprobante = models.FileField(
        upload_to='gastos/comprobantes/', blank=True, null=True,
        verbose_name=_('Receipt')
    )
    notas       = models.TextField(blank=True, verbose_name=_('Notes'))
    fecha_registro    = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-fecha_registro']
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')

    def __str__(self):
        return f'{self.titulo} — {self.moneda} {self.monto}'

    @property
    def icono(self):
        return CATEGORIA_ICONS.get(self.categoria, 'bi-cash')

    @property
    def color(self):
        return CATEGORIA_COLORS.get(self.categoria, '#374151')

    @property
    def estado_badge(self):
        return {
            'pendiente': 'warning',
            'pagado':    'success',
            'cancelado': 'secondary',
        }.get(self.estado, 'secondary')


class Partner(models.Model):
    nombre = models.CharField(max_length=120)
    logo   = models.ImageField(upload_to='partners/')
    url    = models.URLField(blank=True)
    orden  = models.PositiveSmallIntegerField(default=0, help_text='Menor número = primero')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Partner'
        verbose_name_plural = 'Partners'

    def __str__(self):
        return self.nombre
