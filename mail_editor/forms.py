from django import forms
from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.template import loader
from django.utils.translation import gettext as _

from ckeditor.widgets import CKEditorWidget

from .models import MailTemplate
from .settings import get_choices


class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = ('template_type', 'domain', 'remarks', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
            'template_type': forms.Select(choices=get_choices())
        }

    def clean(self):
        cleaned_data = super().clean()

        template_type = cleaned_data['template_type']
        domain = cleaned_data['domain']
        language = cleaned_data['language']

        existing_templates = (
            self._meta.model.objects
            .filter(template_type=template_type, domain=domain, language=language)
            .values_list("pk", flat=True)
        )

        if not existing_templates:
            return cleaned_data

        if not self.instance.pk or not bool(self.instance.pk in existing_templates):
            raise ValidationError(
                _('A template with this type, language and domain already exists')
            )

        return cleaned_data


    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)

        template = loader.get_template('mail/_outer_table.html')
        # TODO: This only works when sites-framework is installed.
        try:
            current_site = get_current_site(None)
            domain = current_site.domain
        except Exception as e:
            domain = ''
        self.fields['body'].initial = template.render({'domain': domain}, None)
