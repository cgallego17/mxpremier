from django import forms
from django.utils.translation import gettext_lazy as _
from jugadores.models import Jugador


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = [
            'nombre', 'apellidos', 'fecha_nacimiento', 'ciudad_estado',
            'nacionalidad', 'doble_nacionalidad', 'segunda_nacionalidad', 'instagram',
            'equipo_viaje', 'equipo_ciudad_estado',
            'posicion_principal', 'posicion_secundaria', 'es_pitcher',
            'tutor_nombre', 'tutor_apellidos', 'tutor_telefono', 'tutor_email',
        ]
        widgets = {
            'nombre':               forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos':            forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ciudad_estado':        forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad':         forms.Select(attrs={'class': 'form-select'}),
            'doble_nacionalidad':   forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_doble_nacionalidad'}),
            'segunda_nacionalidad': forms.Select(attrs={'class': 'form-select', 'id': 'id_segunda_nacionalidad'}),
            'instagram':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'equipo_viaje':         forms.TextInput(attrs={'class': 'form-control'}),
            'equipo_ciudad_estado': forms.TextInput(attrs={'class': 'form-control'}),
            'posicion_principal':   forms.Select(attrs={'class': 'form-select'}),
            'posicion_secundaria':  forms.Select(attrs={'class': 'form-select'}),
            'es_pitcher':           forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tutor_nombre':         forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_apellidos':      forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_telefono':       forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_email':          forms.EmailInput(attrs={'class': 'form-control'}),
        }

    OPTIONAL_FIELDS = {'instagram', 'doble_nacionalidad', 'segunda_nacionalidad', 'es_pitcher'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.OPTIONAL_FIELDS:
                field.required = True

    def clean(self):
        cleaned = super().clean()
        doble = cleaned.get('doble_nacionalidad')
        segunda = cleaned.get('segunda_nacionalidad')
        if doble and not segunda:
            self.add_error('segunda_nacionalidad', _('Select the second nationality.'))
        if not doble:
            cleaned['segunda_nacionalidad'] = None
        return cleaned
