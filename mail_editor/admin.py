from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import settings
from .forms import MailTemplateForm
from .models import MailTemplate


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ['get_type_display', 'language', 'get_description', 'subject']
    list_filter = ['template_type', 'language']
    readonly_fields = ('get_variable_help_text', )
    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            (None, {
                'fields': [
                    'template_type', 'language', 'subject', 'body',
                ],
            }),
            (_('Help'), {
                'fields': [
                    'get_variable_help_text', 'remarks',
                ],
            }),
        ]
        return fieldset

    def get_type_display(self, obj):
        conf = settings.TEMPLATES.get(obj.template_type)
        return conf.get('name')
    get_type_display.short_description = _('Template Type')

    def get_description(self, obj):
        conf = settings.TEMPLATES.get(obj.template_type)
        return conf.get('description')
    get_description.short_description = _('Type Description')

    def get_variable_help_text(self, obj):
        if not obj.template_type:
            return _('Please save the template to load the variables')
        return obj.get_variable_help_text()
    get_variable_help_text.short_description = _('Subject variables')
