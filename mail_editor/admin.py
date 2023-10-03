from django.conf import settings as django_settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import settings
from .forms import MailTemplateForm
from .models import MailTemplate


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'get_type_display',
        'language',
        'domain',
        'get_description',
        'subject',
        'base_template_path',
    )
    list_filter = ('template_type', 'language', 'domain',)
    readonly_fields = ('get_variable_help_text', )

    search_fields = ("internal_name", "template_type", "subject",)

    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            (None, {
                'fields': [
                    'template_type',
                    'language',
                    'domain',
                    'subject',
                    'body',
                    'base_template_path',
                ],
            }),
            (_('Help'), {
                'fields': ['get_variable_help_text', 'remarks',],
            }),
        ]
        return fieldset

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "language":
            # dynamically set choices and return a choice field
            db_field.choices = django_settings.LANGUAGES
            return self.formfield_for_choice_field(db_field, request, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

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
