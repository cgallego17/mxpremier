from django import forms
from django.utils.translation import gettext_lazy as _
from landing.models import SponsorInquiry


class SponsorForm(forms.ModelForm):
    class Meta:
        model = SponsorInquiry
        fields = [
            'company_name', 'contact_name', 'email', 'phone', 'website',
            'interest_teams', 'interest_players', 'interest_showcases',
            'interest_tournaments', 'interest_full_program',
            'budget',
            'goal_brand_awareness', 'goal_youth_athletes', 'goal_community',
            'goal_marketing', 'goal_international',
            'activation_logo', 'activation_event', 'activation_social',
            'activation_onsite',
            'logo', 'notes', 'wants_proposal',
        ]

    OPTIONAL_FIELDS = {
        'website', 'budget', 'logo', 'notes', 'wants_proposal',
        'interest_teams', 'interest_players', 'interest_showcases',
        'interest_tournaments', 'interest_full_program',
        'goal_brand_awareness', 'goal_youth_athletes', 'goal_community',
        'goal_marketing', 'goal_international',
        'activation_logo', 'activation_event', 'activation_social',
        'activation_onsite',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.OPTIONAL_FIELDS:
                field.required = True

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_('Logo must be under 5 MB.'))
            if not logo.content_type.startswith('image/'):
                raise forms.ValidationError(_('Only image files are allowed.'))
        return logo

    def clean_company_name(self):
        value = self.cleaned_data.get('company_name', '').strip()
        if len(value) < 2:
            raise forms.ValidationError(_('Must be at least 2 characters.'))
        return value

    def clean_phone(self):
        value = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) < 7:
            raise forms.ValidationError(_('Enter a valid phone number.'))
        return value
