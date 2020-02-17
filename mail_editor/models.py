import logging
import os
import copy
import subprocess
from tempfile import NamedTemporaryFile

from django.conf import settings as django_settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.template import Context, Template, loader
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from . import settings
from .mail_template import validate_template
from .node import locate_package_json
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
        mail_template = self.filter(
            template_type=template_type
        ).filter(
            Q(language=language)|Q(language='')
        ).order_by('-language').first()
        if mail_template is None:
            raise MailTemplate.DoesNotExist()
        return mail_template


@python_2_unicode_compatible
class MailTemplate(models.Model):
    template_type = models.CharField(_('type'), max_length=50)
    language = models.CharField(max_length=10, choices=django_settings.LANGUAGES, blank=True)

    remarks = models.TextField(_('remarks'), blank=True, default='', help_text=_('Extra information about the template'))
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'), help_text=_('Add the body with {{variable}} placeholders'))

    objects = MailTemplateManager()

    CONFIG = {}
    CHOICES = None

    class Meta:
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')
        unique_together = (('template_type', 'language'), )

    def __init__(self, *args, **kwargs):
        super(MailTemplate, self).__init__(*args, **kwargs)
        self.CONFIG = settings.get_config()

    def __str__(self):
        return self.template_type

    def clean(self):
        validate_template(self)

    def render(self, context, subj_context=None):
        base_context = getattr(django_settings, 'MAIL_EDITOR_BASE_CONTEXT', {})

        if not subj_context:
            subj_context = context

        tpl_subject = Template(self.subject)
        tpl_body = Template(self.body)

        ctx = Context(base_context)
        ctx.update(context)
        subj_ctx = Context(base_context)
        subj_ctx.update(subj_context)

        partial_body = tpl_body.render(ctx)
        template = loader.get_template('mail/_base.html')
        try:
            current_site = get_current_site(None)
            domain = current_site.domain
        except Exception as e:
            domain = ''

        body_context = copy.deepcopy(base_context)
        body_context.update({'domain': domain, 'content': partial_body})
        body = template.render(body_context, None)

        # TODO: I made the package.json stuff optional. Maybe it should be removed completely since it adds 3 settings,
        # seems for a limited use-case, and it uses subproces...
        package_json = locate_package_json()
        if package_json:
            env = os.environ.copy()
            if settings.ADD_BIN_PATH:
                env['PATH'] = '{}:{}'.format(env['PATH'], settings.BIN_PATH)

            with NamedTemporaryFile() as temp_file:
                temp_file.write(bytes(body, 'UTF-8'))
                process = subprocess.Popen(
                    "inject-inline-styles.js {}".format(temp_file.name), shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    env=env, universal_newlines=True, cwd=os.path.dirname(package_json)
                )

                body, err = process.communicate()
                if err:
                    raise Exception(err)

        return tpl_subject.render(subj_ctx), mark_safe(body)

    def build_message(self, to_addresses, context, subj_context=None, txt=False, attachments=None,
                      cc_addresses=None, bcc_addresses=None):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.

        @param attachments: List of tuples, where the tuple can be one of two forms:
                            `(<absolute file path>, [mime type])` or
                            `(<filename>, <content>, [mime type])`
        """
        subject, body = self.render(context, subj_context)
        text_body = txt or strip_tags(body)

        email_message = EmailMultiAlternatives(
            subject=subject, body=text_body, from_email=django_settings.DEFAULT_FROM_EMAIL,
            to=to_addresses, cc=cc_addresses, bcc=bcc_addresses)
        email_message.attach_alternative(body, 'text/html')

        if attachments:
            for attachment in attachments:
                if not attachment or not isinstance(attachment, tuple):
                    raise ValueError('Attachments should be passed as a list of tuples.')
                if os.path.isabs(attachment[0]):
                    email_message.attach_file(*attachment)
                else:
                    email_message.attach(*attachment)

        return email_message

    def send_email(self, to_addresses, context, subj_context=None, txt=False, attachments=None,
                   cc_addresses=None, bcc_addresses=None):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.

        @param attachments: List of tuples, where the tuple can be one of two forms:
                            `(<absolute file path>, [mime type])` or
                            `(<filename>, <content>, [mime type])`
        """
        email_message = self.build_message(to_addresses, context, subj_context=subj_context, txt=txt,
                        attachments=attachments, cc_addresses=cc_addresses, bcc_addresses=bcc_addresses)
        return email_message.send()

    def get_variable_help_text(self):
        return variable_help_text(self.template_type)
