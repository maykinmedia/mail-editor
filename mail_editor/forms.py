from django import forms

from ckeditor.widgets import CKEditorWidget

from .models import Mail, MailTemplate


class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = ('template_type', 'remarks', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
        }


class MailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ('to', 'cc', 'bcc', 'subject', 'body')
        widgets = {
            'body': CKEditorWidget(config_name='mail_editor'),
        }
