import datetime
from django import forms
from django.utils.translation import gettext_lazy as _
from jugadores.models import Jugador
from .models import Partner


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = [
            'nombre', 'apellidos', 'fecha_nacimiento',
            'pais', 'estado', 'ciudad',
            'nacionalidad', 'doble_nacionalidad', 'segunda_nacionalidad', 'instagram',
            'equipo_viaje', 'equipo_ciudad_estado',
            'posicion_principal', 'posicion_secundaria', 'es_pitcher',
            'tutor_nombre', 'tutor_apellidos', 'tutor_telefono', 'tutor_email',
        ]
        widgets = {
            'nombre':               forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos':            forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pais':                 forms.Select(attrs={'class': 'form-select'}),
            'estado':               forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad':               forms.TextInput(attrs={'class': 'form-control'}),
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

    OPTIONAL_FIELDS = {'instagram', 'doble_nacionalidad', 'segunda_nacionalidad', 'es_pitcher', 'estado'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.OPTIONAL_FIELDS:
                field.required = True

    def clean_nombre(self):
        value = self.cleaned_data.get('nombre', '').strip()
        if len(value) < 2:
            raise forms.ValidationError(_('Must be at least 2 characters.'))
        return value

    def clean_apellidos(self):
        value = self.cleaned_data.get('apellidos', '').strip()
        if len(value) < 2:
            raise forms.ValidationError(_('Must be at least 2 characters.'))
        return value

    def clean_ciudad(self):
        value = self.cleaned_data.get('ciudad', '').strip()
        if value and len(value) < 2:
            raise forms.ValidationError(_('Must be at least 2 characters.'))
        return value

    def clean_fecha_nacimiento(self):
        dob = self.cleaned_data.get('fecha_nacimiento')
        if not dob:
            return dob
        today = datetime.date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if dob > today:
            raise forms.ValidationError(_('Date of birth cannot be in the future.'))
        if age > 18:
            raise forms.ValidationError(_('Player must be 18 years old or younger.'))
        return dob

    def clean_tutor_email(self):
        email = self.cleaned_data.get('tutor_email', '').strip().lower()
        qs = Jugador.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('A player with this email is already registered.'))
        return email

    def clean(self):
        cleaned = super().clean()
        doble = cleaned.get('doble_nacionalidad')
        segunda = cleaned.get('segunda_nacionalidad')
        if doble and not segunda:
            self.add_error('segunda_nacionalidad', _('Select the second nationality.'))
        if not doble:
            cleaned['segunda_nacionalidad'] = None
        return cleaned


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['nombre', 'logo', 'url', 'orden', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'url':    forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'orden':  forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
