from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .forms import MailTemplateForm
from .models import MailTemplate


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_type']
    list_filter = ['template_type']
    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            ('', {
                'fields': [
                    'template_type', 'remarks', 'subject', 'body'
                ],
                'description': obj.get_variable_help_text(),
            }),
        ]
        return fieldset
