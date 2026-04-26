from django.db import models


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
