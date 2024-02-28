import logging

from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import MailTemplate
from .settings import settings

try:
    from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
except ImportError:
    from django.template.base import TemplateDoesNotExist, TemplateSyntaxError


logger = logging.getLogger(__name__)


def find_template(template_name, language=None):
    if language:
        template, _created = MailTemplate.objects.get_or_create(
            template_type=template_name,
            language=language,
            defaults={
                "subject": get_subject(template_name),
                "body": get_body(template_name),
                "base_template_path": get_base_template_path(template_name),
            },
        )
    else:
        base_qs = MailTemplate.objects.filter(
            template_type=template_name, language__isnull=True
        )
        if base_qs.exists():
            template = base_qs.first()
        else:
            template = MailTemplate.objects.create(
                template_type=template_name,
                subject=get_subject(template_name),
                body=get_body(template_name),
                base_template_path=get_base_template_path(template_name),
            )

    return template


def get_subject(template_name):
    config = settings.TEMPLATES

    template_config = config.get(template_name)
    if template_config:
        subject = template_config.get("subject_default")
        if subject:
            return subject

    return _("Please fix this template")


def get_body(template_name):
    config = settings.TEMPLATES

    template_config = config.get(template_name)
    default = _("Your content here...")
    if template_config:
        body = template_config.get("body_default")
        if body:
            default = body

    template = loader.get_template("mail/_outer_table.html")
    current_site = get_current_site(None)
    return template.render(
        {"domain": current_site.domain, "default": mark_safe(default)}, None
    )


def get_base_template_path(template_name):
    config = settings.TEMPLATES

    template_config = config.get(template_name)
    if template_config:
        return template_config.get("base_template", "")
    return ""


def base_template_loader(template_path, context):
    default_path = "mail/_base.html"

    if not template_path:
        template_path = default_path

    try:
        return loader.render_to_string(template_path, context)
    except (TemplateDoesNotExist, TemplateSyntaxError) as e:
        logging.exception("Base template could not be rendered")
        return loader.render_to_string(default_path, context)
