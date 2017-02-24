from django.contrib import admin

from .forms import MailTemplateForm
from .models import MailTemplate
from .utils import variable_help_text


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_type']
    list_filter = ['template_type']
    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        description = ''

        if request.POST.get('template_type'):
            description = variable_help_text(request.POST.get('template_type'))
        if obj:
            description = obj.get_variable_help_text()

        fieldset = [
            ('', {
                'fields': [
                    'template_type', 'remarks', 'subject', 'body'
                ],
                'description': description,
            }),
        ]
        return fieldset
