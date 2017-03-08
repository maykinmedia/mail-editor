from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader

from ckeditor.widgets import CKEditorWidget

from .models import Mail, MailTemplate
from .settings import get_choices


class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = ('template_type', 'remarks', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
            'template_type': forms.Select(choices=get_choices())
        }

    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)

        template = loader.get_template('mail/_outer_table.html')
        current_site = get_current_site(None)
        self.fields['body'].initial = template.render({'domain': current_site.domain}, None)


class MailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ('to', 'cc', 'bcc', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
        }
