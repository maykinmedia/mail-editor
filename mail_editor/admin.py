from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .forms import MailTemplateForm
from .models import MailTemplate
from .utils import variable_help_text


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_type']
    list_filter = ['template_type']
    readonly_fields = ('get_variable_help_text', )
    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            (None, {
                'fields': [
                    'template_type', 'subject', 'body',
                ],
            }),
            (_('Help'), {
                'fields': [
                    'get_variable_help_text', 'remarks',
                ],
            }),
        ]
        return fieldset

    def get_variable_help_text(self, obj):
        if not obj.template_type:
            return _('Please save the template to load the variables')
        return obj.get_variable_help_text()
    get_variable_help_text.short_description = _('Subject variables')