from django.conf import settings as django_settings
from django.contrib import admin, messages
from django.urls import re_path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import MailTemplateForm
from .models import MailTemplate
from .settings import settings
from .views import (
    TemplateBrowserPreviewView,
    TemplateEmailPreviewFormView,
    TemplateVariableView,
)


@admin.register(MailTemplate)
class MailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "template_type",
        "internal_name",
        "language",
        "get_preview_link",
        "get_description",
        "subject",
        "base_template_path",
    )
    list_filter = (
        "template_type",
        "language",
        "internal_name",
    )
    readonly_fields = (
        "get_variable_help_text",
        "get_preview_link",
    )
    search_fields = (
        "internal_name",
        "template_type",
        "subject",
    )
    actions = [
        "reload_templates",
    ]

    form = MailTemplateForm

    def get_fieldsets(self, request, obj=None):
        fieldset = [
            (
                None,
                {
                    "fields": [
                        "internal_name",
                        "template_type",
                        "language",
                        "get_preview_link",
                        "subject",
                        "body",
                        "base_template_path",
                    ],
                },
            ),
            (
                _("Help"),
                {
                    "fields": [
                        "get_variable_help_text",
                        "remarks",
                    ],
                },
            ),
        ]
        return fieldset

    def get_preview_link(self, obj=None):
        url = self.get_preview_url(obj)
        if url:
            return format_html('<a href="{}">{}</a>', url, _("Open"))
        else:
            return _("Save to enable preview")

    get_preview_link.short_description = _("Preview")

    def get_preview_url(self, obj=None):
        if obj and obj.pk:
            return reverse("admin:mailtemplate_preview", kwargs={"pk": obj.id})

    def get_urls(self):
        # reminder: when using admin templates also add self.admin_site.each_context(request)
        return [
            re_path(
                r"^variables/(?P<template_type>[-\w]+)/$",
                self.admin_site.admin_view(TemplateVariableView.as_view()),
                name="mailtemplate_variables",
            ),
            re_path(
                r"^preview/(?P<pk>[0-9]+)/$",
                self.admin_site.admin_view(TemplateBrowserPreviewView.as_view()),
                name="mailtemplate_render",
            ),
            re_path(
                r"^email/(?P<pk>[0-9]+)/$",
                self.admin_site.admin_view(TemplateEmailPreviewFormView.as_view()),
                name="mailtemplate_preview",
            ),
        ] + super().get_urls()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "language":
            # dynamically set choices and return a choice field
            db_field.choices = django_settings.LANGUAGES
            return self.formfield_for_choice_field(db_field, request, **kwargs)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_type_display(self, obj):
        conf = settings.TEMPLATES.get(obj.template_type)
        return conf.get("name")

    get_type_display.short_description = _("Template Type")

    def get_description(self, obj):
        conf = settings.TEMPLATES.get(obj.template_type)
        return conf.get("description")

    get_description.short_description = _("Type Description")

    def get_variable_help_text(self, obj):
        if not obj.template_type:
            return _("Please save the template to load the variables")
        return obj.get_variable_help_text()

    get_variable_help_text.short_description = _("Subject variables")

    def reload_templates(self, request, queryset):
        for template in queryset:
            template.reload_template()
            template.save()
            self.message_user(
                request,
                _("Template '{name}' is reset").format(name=template.template_type),
                level=messages.SUCCESS,
            )

    reload_templates.short_description = _(
        "Reset templates (WARNING: overwrites current content)"
    )
