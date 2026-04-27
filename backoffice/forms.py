import datetime
from django import forms
from django.utils.translation import gettext_lazy as _
from backoffice.models import Partner
from jugadores.models import Jugador
from .models import Partner, Gasto


class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = [
            'nombre', 'apellidos', 'fecha_nacimiento',
            'pais', 'estado', 'ciudad',
            'nacionalidad', 'doble_nacionalidad', 'segunda_nacionalidad', 'instagram',
            'equipo_viaje', 'equipo_pais', 'equipo_estado', 'equipo_ciudad',
            'posicion_principal', 'posicion_secundaria', 'es_pitcher',
            'telefono',
            'tutor_nombre', 'tutor_apellidos', 'tutor_telefono', 'tutor_email',
        ]
        widgets = {
            'telefono':             forms.TextInput(attrs={'class': 'form-control'}),
            'nombre':               forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos':            forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento':     forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'pais':                 forms.Select(attrs={'class': 'form-select', 'id': 'id_pais'}),
            'estado':               forms.Select(attrs={'class': 'form-select', 'id': 'id_estado'}),
            'ciudad':               forms.Select(attrs={'class': 'form-select', 'id': 'id_ciudad'}),
            'nacionalidad':         forms.Select(attrs={'class': 'form-select'}),
            'doble_nacionalidad':   forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_doble_nacionalidad'}),
            'segunda_nacionalidad': forms.Select(attrs={'class': 'form-select', 'id': 'id_segunda_nacionalidad'}),
            'instagram':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username'}),
            'equipo_viaje':         forms.TextInput(attrs={'class': 'form-control'}),
            'equipo_pais':          forms.Select(attrs={'class': 'form-select', 'id': 'id_equipo_pais'}),
            'equipo_estado':        forms.Select(attrs={'class': 'form-select', 'id': 'id_equipo_estado'}),
            'equipo_ciudad':        forms.Select(attrs={'class': 'form-select', 'id': 'id_equipo_ciudad'}),
            'posicion_principal':   forms.Select(attrs={'class': 'form-select'}),
            'posicion_secundaria':  forms.Select(attrs={'class': 'form-select'}),
            'es_pitcher':           forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tutor_nombre':         forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_apellidos':      forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_telefono':       forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_email':          forms.EmailInput(attrs={'class': 'form-control'}),
        }

    OPTIONAL_FIELDS = {'instagram', 'doble_nacionalidad', 'segunda_nacionalidad', 'es_pitcher', 'estado', 'telefono', 'equipo_pais', 'equipo_estado', 'equipo_ciudad', 'ciudad'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.OPTIONAL_FIELDS:
                field.required = True
        # Populate estado/ciudad choices from DB so the Select widget accepts submitted values.
        # JS fetches the full option list via AJAX; here we ensure currently-saved values
        # are valid options so Django validation doesn't reject them.
        from jugadores.models import Estado, Ciudad
        pais_val = self.data.get('pais') or (self.instance.pais if self.instance.pk else '')
        estado_val = self.data.get('estado') or (self.instance.estado if self.instance.pk else '')
        if pais_val:
            state_qs = Estado.objects.filter(pais__codigo=pais_val).values_list('codigo', 'nombre').order_by('nombre')
            self.fields['estado'].widget.choices = [('', '—')] + list(state_qs)
            if estado_val:
                city_qs = Ciudad.objects.filter(
                    estado__codigo=estado_val, estado__pais__codigo=pais_val
                ).values_list('nombre', 'nombre').order_by('nombre')
                self.fields['ciudad'].widget.choices = [('', '—')] + list(city_qs)
            else:
                self.fields['ciudad'].widget.choices = [('', '—')]
        else:
            self.fields['estado'].widget.choices = [('', '—')]
            self.fields['ciudad'].widget.choices = [('', '—')]
        # Same for equipo
        equipo_pais_val = self.data.get('equipo_pais') or (self.instance.equipo_pais if self.instance.pk else '')
        equipo_estado_val = self.data.get('equipo_estado') or (self.instance.equipo_estado if self.instance.pk else '')
        if equipo_pais_val:
            eq_state_qs = Estado.objects.filter(pais__codigo=equipo_pais_val).values_list('codigo', 'nombre').order_by('nombre')
            self.fields['equipo_estado'].widget.choices = [('', '—')] + list(eq_state_qs)
            if equipo_estado_val:
                eq_city_qs = Ciudad.objects.filter(
                    estado__codigo=equipo_estado_val, estado__pais__codigo=equipo_pais_val
                ).values_list('nombre', 'nombre').order_by('nombre')
                self.fields['equipo_ciudad'].widget.choices = [('', '—')] + list(eq_city_qs)
            else:
                self.fields['equipo_ciudad'].widget.choices = [('', '—')]
        else:
            self.fields['equipo_estado'].widget.choices = [('', '—')]
            self.fields['equipo_ciudad'].widget.choices = [('', '—')]

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
        if dob > today:
            raise forms.ValidationError(_('Date of birth cannot be in the future.'))
        return dob

    def clean_tutor_email(self):
        email = self.cleaned_data.get('tutor_email', '').strip().lower()
        # Buscar duplicados en tutor_email, no en email del jugador
        qs = Jugador.objects.filter(tutor_email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(_('A player with this guardian email is already registered.'))
        # También verificar si el email ya existe como email de otro jugador
        # (porque en la vista se asigna tutor_email a email si email está vacío)
        qs_email = Jugador.objects.filter(email=email)
        if self.instance.pk:
            qs_email = qs_email.exclude(pk=self.instance.pk)
        if qs_email.exists():
            raise forms.ValidationError(_('This email is already registered.'))
        return email

    def clean(self):
        cleaned = super().clean()
        doble = cleaned.get('doble_nacionalidad')
        segunda = cleaned.get('segunda_nacionalidad')
        if doble and not segunda:
            self.add_error('segunda_nacionalidad', _('Select the second nationality.'))
        if not doble:
            cleaned['segunda_nacionalidad'] = None


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = [
            'titulo', 'categoria', 'monto', 'moneda', 'fecha',
            'metodo_pago', 'estado', 'comprobante', 'notas'
        ]
        widgets = {
            'titulo':        forms.TextInput(attrs={'class': 'form-control'}),
            'categoria':     forms.Select(attrs={'class': 'form-select'}),
            'monto':         forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'moneda':        forms.Select(attrs={'class': 'form-select'}),
            'fecha':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'metodo_pago':   forms.Select(attrs={'class': 'form-select'}),
            'estado':        forms.Select(attrs={'class': 'form-select'}),
            'comprobante':   forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notas':         forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

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
