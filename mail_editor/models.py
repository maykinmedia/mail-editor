import copy
import logging
import os
from email.mime.image import MIMEImage

from django.conf import settings as django_settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.template import Context, Template
from django.utils.html import strip_tags
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .mail_template import validate_template
from .process import process_html
from .settings import get_config, settings
from .utils import variable_help_text

logger = logging.getLogger(__name__)


class MailTemplateManager(models.Manager):
    def get_for_language(self, template_type, language):
        """
        Returns the `MailTemplate` for the given type in the given language. If the language does not exist, it
        attempts to find and return the fallback (no language) instance.

        :param template_type:
        :param language:
        :return:
        """
        mail_template = (
            self.filter(template_type=template_type)
            .filter(Q(language=language) | Q(language=""))
            .order_by("-language")
            .first()
        )
        if mail_template is None:
            raise MailTemplate.DoesNotExist()
        return mail_template


class MailTemplate(models.Model):
    internal_name = models.CharField(max_length=255, default="", blank=True)
    template_type = models.CharField(_("type"), max_length=50)
    language = models.CharField(max_length=10, blank=True, null=True)

    remarks = models.TextField(
        _("remarks"),
        blank=True,
        default="",
        help_text=_("Extra information about the template"),
    )
    subject = models.CharField(_("subject"), max_length=255)
    body = models.TextField(
        _("body"), help_text=_("Add the body with {{variable}} placeholders")
    )
    base_template_path = models.CharField(
        _("Base template path"),
        max_length=200,
        null=True,
        blank=True,
        help_text="Leave empty for default template. Override to load a different template.",
    )

    objects = MailTemplateManager()

    CHOICES = None

    class Meta:
        verbose_name = _("mail template")
        verbose_name_plural = _("mail templates")

    def __init__(self, *args, **kwargs):
        super(MailTemplate, self).__init__(*args, **kwargs)
        self.config = get_config().get(self.template_type) or dict()

    def __str__(self):
        if self.internal_name:
            return self.internal_name
        elif self.language:
            return f"{self.template_type} - {self.language}"

        return self.template_type

    def clean(self):
        validate_template(self)

        if settings.UNIQUE_LANGUAGE_TEMPLATES:
            queryset = self.__class__.objects.filter(
                language=self.language, template_type=self.template_type
            ).values_list("pk", flat=True)

            if queryset.exists() and not (self.pk and self.pk in queryset):
                raise ValidationError(
                    _("Mail template with this type and language already exists")
                )

    def reload_template(self):
        from .helpers import get_base_template_path, get_body, get_subject

        self.subject = get_subject(self.template_type)
        self.body = get_body(self.template_type)
        self.base_template_path = get_base_template_path(self.template_type)

    def get_base_context(self):
        base_context = copy.deepcopy(settings.BASE_CONTEXT)
        dynamic = settings.DYNAMIC_CONTEXT
        if dynamic:
            base_context.update(dynamic())
        return base_context

    def get_preview_contexts(self):
        base_context = self.get_base_context()

        def _get_context(section):
            context = {}
            for var in section:
                value = var.example or base_context.get(var.name, "")
                if not value:
                    value = "--{}--".format(var.name)
                context[var.name] = value
            return context

        body = _get_context(self.config["body"])
        subject = _get_context(self.config["subject"])
        return subject, body

    def render(self, context, subj_context=None):
        base_context = self.get_base_context()

        if not subj_context:
            subj_context = context

        tpl_subject = Template(self.subject)
        tpl_body = Template(self.body)

        try:
            current_site = get_current_site(None)
            domain = current_site.domain
        except Exception as e:
            domain = ""

        base_context.update(context)
        base_context.update({"domain": domain})

        ctx = Context(base_context)
        ctx.update(context)
        ctx.update({"domain": domain})
        subj_ctx = Context(base_context)
        subj_ctx.update(subj_context)

        partial_body = tpl_body.render(ctx)
        template_function = import_string(settings.BASE_TEMPLATE_LOADER)

        body_context = copy.deepcopy(base_context)
        body_context.update({"content": partial_body})
        body = template_function(self.base_template_path, body_context)

        return tpl_subject.render(subj_ctx), mark_safe(body)

    def build_message(
        self,
        to_addresses,
        context,
        subj_context=None,
        txt=False,
        attachments=None,
        cc_addresses=None,
        bcc_addresses=None,
    ):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.

        @param attachments: List of tuples, where the tuple can be one of two forms:
                            `(<absolute file path>, [mime type])` or
                            `(<filename>, <content>, [mime type])`
        """
        subject, body = self.render(context, subj_context)

        result = process_html(body, settings.BASE_HOST)

        text_body = txt or strip_tags(result.html)

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=to_addresses,
            cc=cc_addresses,
            bcc=bcc_addresses,
        )
        email_message.attach_alternative(result.html, "text/html")
        email_message.mixed_subtype = "related"

        if attachments:
            for attachment in attachments:
                if not attachment or not isinstance(attachment, tuple):
                    raise ValueError(
                        "Attachments should be passed as a list of tuples."
                    )
                if os.path.isabs(attachment[0]):
                    email_message.attach_file(*attachment)
                else:
                    email_message.attach(*attachment)

        if result.cid_attachments:
            for att in result.cid_attachments:
                subtype = att.content_type.split("/", maxsplit=1)
                assert subtype[0] == "image"
                mime_image = MIMEImage(att.content, _subtype=subtype[1])
                mime_image.add_header("Content-ID", f"<{att.cid}>")
                email_message.attach(mime_image)

        return email_message

    def send_email(
        self,
        to_addresses,
        context,
        subj_context=None,
        txt=False,
        attachments=None,
        cc_addresses=None,
        bcc_addresses=None,
    ):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.

        @param attachments: List of tuples, where the tuple can be one of two forms:
                            `(<absolute file path>, [mime type])` or
                            `(<filename>, <content>, [mime type])`
        """
        email_message = self.build_message(
            to_addresses,
            context,
            subj_context=subj_context,
            txt=txt,
            attachments=attachments,
            cc_addresses=cc_addresses,
            bcc_addresses=bcc_addresses,
        )
        return email_message.send()

    def get_variable_help_text(self):
        return variable_help_text(self.template_type)
