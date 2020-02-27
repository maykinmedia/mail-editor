from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import MailTemplate


def find_template(template_name):
    template, created = MailTemplate.objects.get_or_create(template_type=template_name, defaults={
        'subject': get_subject(template_name),
        'body': get_body(template_name)
    })

    return template


def get_subject(template_name):
    config = settings.MAIL_EDITOR_TEMPLATES

    template_config = config.get(template_name)
    if template_config:
        subject = template_config.get('subject_default')
        if subject:
            return subject

    return _('Please fix this template')


def get_body(template_name):
    config = settings.MAIL_EDITOR_TEMPLATES

    template_config = config.get(template_name)
    default = _('Your content here...')
    if template_config:
        body = template_config.get('body_default')
        if body:
            default = body

    template = loader.get_template('mail/_outer_table.html')
    current_site = get_current_site(None)
    return template.render({'domain': current_site.domain, 'default': mark_safe(default)}, None)
