from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import Context, Template
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from .mail_template import validate_template
from .settings import get_config
from .utils import variable_help_text


@python_2_unicode_compatible
class Mail(models.Model):
    to = models.TextField()
    cc = models.TextField(blank=True)
    bcc = models.TextField(blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('email')
        verbose_name_plural = _('emails')
        ordering = ('-pk',)

    def __str__(self):
        return self.subject


@python_2_unicode_compatible
class MailTemplate(models.Model):
    template_type = models.CharField(_('type'), max_length=50, unique=True)

    remarks = models.TextField(_('remarks'), blank=True, default='', help_text=_('Extra information about the template'))
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'), help_text=_('Add the body with {{variable}} placeholders'))

    CONFIG = {}
    CHOICES = None

    class Meta:
        verbose_name = _('mail template')
        verbose_name_plural = _('mail templates')

    def __init__(self, *args, **kwargs):
        super(MailTemplate, self).__init__(*args, **kwargs)

        # fields = self._meta.get_field('template_type')
        # fields.choices = get_choices()

        self.CONFIG = get_config()

    def __str__(self):
        return self.template_type

    def clean(self):
        validate_template(self)

    def render(self, context, subj_context=None):
        if not subj_context:
            subj_context = context

        tpl_subject = Template(self.subject)
        tpl_body = Template(self.body)

        ctx = Context(context)
        subj_ctx = Context(subj_context)
        return tpl_subject.render(subj_ctx), tpl_body.render(ctx)

    def send_email(self, to, context, subj_context=None, txt=False):
        """
        You can pass the context only. We will pass the context to the subject context when we don't
        have a subject context.
        """
        subject, body = self.render(context, subj_context)
        text_body = ''
        if txt:
            text_body = strip_tags(body)

        email_message = EmailMultiAlternatives(subject=subject, body=text_body, from_email=settings.DEFAULT_FROM_EMAIL, to=to)
        email_message.attach_alternative(body, 'text/html')
        email_message.send()

    def get_variable_help_text(self):
        return variable_help_text(self.template_type)
