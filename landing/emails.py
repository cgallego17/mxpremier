"""Email sending utilities for player registration and sponsor inquiries."""
import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

SITE_URL = getattr(settings, 'SITE_URL', 'https://www.mxbaseball.com')
ADMIN_EMAIL = getattr(settings, 'ADMIN_EMAIL', '')


def _send(subject, html, to, reply_to=None):
    if not to:
        return
    try:
        msg = EmailMessage(
            subject=subject,
            body=html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to] if isinstance(to, str) else to,
            reply_to=[reply_to] if reply_to else None,
        )
        msg.content_subtype = 'html'
        msg.send(fail_silently=False)
    except (SMTPException, OSError, TimeoutError) as exc:
        logger.error('Email send failed to %s: %s', to, exc)


def send_registro_emails(jugador, lang='en'):
    """Send registration confirmation to the player and a notification to admin."""
    ctx = {'jugador': jugador, 'site_url': SITE_URL, 'lang': lang}
    recipient = jugador.tutor_email or jugador.email

    if recipient:
        with translation.override(lang):
            subject = _('Your Estado 33 registration is confirmed ✓')
            html = render_to_string('emails/registro_confirmacion.html', ctx)
        _send(subject, html, recipient)

    if ADMIN_EMAIL:
        with translation.override('en'):
            html = render_to_string('emails/registro_admin.html', ctx)
        _send(
            f'New registration: {jugador.nombre} {jugador.apellidos}',
            html,
            ADMIN_EMAIL,
            reply_to=recipient,
        )


def send_sponsor_emails(sponsor_obj, lang='en'):
    """Send sponsorship inquiry confirmation to sponsor and a notification to admin."""
    ctx = {'sponsor': sponsor_obj, 'site_url': SITE_URL, 'lang': lang}

    if sponsor_obj.email:
        with translation.override(lang):
            subject = _('Sponsorship Inquiry Received — Estado 33')
            html = render_to_string('emails/sponsor_confirmacion.html', ctx)
        _send(subject, html, sponsor_obj.email, reply_to=ADMIN_EMAIL or None)

    if ADMIN_EMAIL:
        with translation.override('en'):
            html = render_to_string('emails/sponsor_admin.html', ctx)
        _send(
            f'New sponsor inquiry: {sponsor_obj.company_name}',
            html,
            ADMIN_EMAIL,
            reply_to=sponsor_obj.email or None,
        )
