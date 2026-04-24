from django.contrib import admin
from .models import Jugador


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = (
        'apellidos',
        'nombre',
        'email',
        'telefono',
        'edad',
        'get_nacionalidad',
        'doble_nacionalidad',
        'fecha_registro',
    )
    list_filter = ('nacionalidad', 'doble_nacionalidad')
    search_fields = ('nombre', 'apellidos', 'email', 'telefono')
    ordering = ('apellidos', 'nombre')
    readonly_fields = ('fecha_registro',)

    fieldsets = (
        ('Datos Personales', {
            'fields': ('nombre', 'apellidos', 'email', 'telefono', 'edad'),
        }),
        ('Nacionalidad', {
            'fields': (
                'nacionalidad',
                'doble_nacionalidad',
                'segunda_nacionalidad',
            ),
        }),
        ('Registro', {
            'fields': ('fecha_registro',),
        }),
    )

    @admin.display(description='Nacionalidad')
    def get_nacionalidad(self, obj):
        base = obj.get_nacionalidad_display()
        if obj.doble_nacionalidad and obj.segunda_nacionalidad:
            segunda = obj.get_segunda_nacionalidad_display()
            return f'{base} / {segunda}'
        return base
