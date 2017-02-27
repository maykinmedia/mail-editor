from django import forms
from django.template import loader

from ckeditor.widgets import CKEditorWidget

from .settings import get_choices
from .models import Mail, MailTemplate


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

        template = loader.get_template('mail/_base.html')
        self.fields['body'].initial = template.render({}, None)


class MailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ('to', 'cc', 'bcc', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
        }
