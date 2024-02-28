from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader

from ckeditor.widgets import CKEditorWidget

from .models import MailTemplate
from .settings import get_choices


class MailTemplateForm(forms.ModelForm):
    class Meta:
        model = MailTemplate
        fields = ("template_type", "remarks", "subject", "body")
        widgets = {
            "body": CKEditorWidget(config_name="mail_editor"),
            "template_type": forms.Select(choices=[]),
        }

    def __init__(self, *args, **kwargs):
        super(MailTemplateForm, self).__init__(*args, **kwargs)

        self.fields["template_type"].widget.choices = get_choices()

        template = loader.get_template("mail/_outer_table.html")
        # TODO: This only works when sites-framework is installed.
        try:
            current_site = get_current_site(None)
            domain = current_site.domain
        except Exception as e:
            domain = ""

        self.fields["body"].initial = template.render({"domain": domain}, None)
