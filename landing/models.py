from django.db import models
from django.utils.translation import gettext_lazy as _


BUDGET_CHOICES = [
    ('lt2500',   _('Under $2,500')),
    ('2500_5k',  _('$2,500–$5,000')),
    ('5k_10k',   _('$5,000–$10,000')),
    ('gt10k',    _('$10,000+')),
]


class SponsorInquiry(models.Model):
    # ── Company information ───────────────────────────────────
    company_name  = models.CharField(max_length=150, verbose_name=_('Company name'))
    contact_name  = models.CharField(max_length=150, verbose_name=_('Contact name'))
    email         = models.EmailField(verbose_name=_('Email'))
    phone         = models.CharField(max_length=30, verbose_name=_('Phone'))
    website       = models.CharField(max_length=200, blank=True, verbose_name=_('Website / Social media'))

    # ── Sponsorship interest ──────────────────────────────────
    interest_teams        = models.BooleanField(default=False, verbose_name=_('Estado 33 Teams'))
    interest_players      = models.BooleanField(default=False, verbose_name=_('Player Sponsorships'))
    interest_showcases    = models.BooleanField(default=False, verbose_name=_('Showcases / Tryouts'))
    interest_tournaments  = models.BooleanField(default=False, verbose_name=_('Mexico Tournaments'))
    interest_full_program = models.BooleanField(default=False, verbose_name=_('Full Program Partnership'))

    # ── Budget ────────────────────────────────────────────────
    budget = models.CharField(
        max_length=10, choices=BUDGET_CHOICES, blank=True, verbose_name=_('Estimated budget')
    )

    # ── Goals ─────────────────────────────────────────────────
    goal_brand_awareness = models.BooleanField(default=False, verbose_name=_('Brand Awareness'))
    goal_youth_athletes  = models.BooleanField(default=False, verbose_name=_('Support Youth Athletes'))
    goal_community       = models.BooleanField(default=False, verbose_name=_('Community Impact'))
    goal_marketing       = models.BooleanField(default=False, verbose_name=_('Marketing / Exposure'))
    goal_international   = models.BooleanField(default=False, verbose_name=_('International (U.S.–Mexico) Reach'))

    # ── Activation ────────────────────────────────────────────
    activation_logo     = models.BooleanField(default=False, verbose_name=_('Logo on uniforms'))
    activation_event    = models.BooleanField(default=False, verbose_name=_('Event branding'))
    activation_social   = models.BooleanField(default=False, verbose_name=_('Social media promotion'))
    activation_onsite   = models.BooleanField(default=False, verbose_name=_('On-site presence'))

    # ── Final step ────────────────────────────────────────────
    logo          = models.ImageField(upload_to='sponsors/logos/', blank=True, null=True, verbose_name=_('Logo'))
    notes         = models.TextField(blank=True, verbose_name=_('Notes / Ideas'))
    wants_proposal = models.BooleanField(default=False, verbose_name=_('Wants custom proposal'))

    # ── Meta ──────────────────────────────────────────────────
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name=_('Submitted'))

    class Meta:
        verbose_name = _('Sponsor Inquiry')
        verbose_name_plural = _('Sponsor Inquiries')
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.company_name} — {self.contact_name}'


class PageVisit(models.Model):
    ip = models.CharField(max_length=45)
    path = models.CharField(max_length=200)
    user_agent = models.CharField(max_length=300, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    referrer = models.CharField(max_length=300, blank=True)
    is_mobile = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['country_code']),
            models.Index(fields=['ip']),
        ]

    def __str__(self):
        return f'{self.ip} {self.path} {self.timestamp:%Y-%m-%d}'

