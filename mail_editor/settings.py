import warnings

from django.conf import settings as django_settings
from django.utils.module_loading import import_string

from .mail_template import Variable


class Settings(object):
    """
    note: changed to dynamic properties to allow testing with different settings
    """

    @property
    def TEMPLATES(self):
        # Available templates and variables for the mail editor.
        tmp = getattr(django_settings, "MAIL_EDITOR_CONF", {})
        if not tmp:
            tmp = getattr(django_settings, "MAIL_EDITOR_TEMPLATES", {})
            warnings.warn(
                "Setting MAIL_EDITOR_TEMPLATES is deprecated, please use MAIL_EDITOR_CONF.",
                DeprecationWarning,
            )
        return tmp

    @property
    def BASE_CONTEXT(self):
        return getattr(django_settings, "MAIL_EDITOR_BASE_CONTEXT", {})

    @property
    def DYNAMIC_CONTEXT(self):
        """
        callable to return optional extra context
        """
        dynamic = getattr(django_settings, "MAIL_EDITOR_DYNAMIC_CONTEXT", None)
        if dynamic:
            return import_string(dynamic)

    @property
    def BASE_HOST(self):
        """
        protocol, domain and (optional) port, no ending slash

        used to retrieve images for embedding and fix URLs
        """
        return getattr(django_settings, "MAIL_EDITOR_BASE_HOST", "")

    @property
    def BASE_TEMPLATE_LOADER(self):
        return getattr(
            django_settings,
            "MAIL_EDITOR_BASE_TEMPLATE_LOADER",
            "mail_editor.helpers.base_template_loader",
        )

    @property
    def UNIQUE_LANGUAGE_TEMPLATES(self):
        return getattr(django_settings, "MAIL_EDITOR_UNIQUE_LANGUAGE_TEMPLATES", True)


settings = Settings()


def get_choices() -> list[tuple[str, str]]:
    choices = []
    for key, values in settings.TEMPLATES.items():
        choices += [(key, values.get("name", key.title()))]
    return choices


def get_config():
    config = {}
    for key, values in settings.TEMPLATES.items():
        subject_variables = []
        for var in values.get("subject", []):
            subject_variables.append(Variable(**var))

        body_variables = []
        for var in values.get("body", []):
            body_variables.append(Variable(**var))

        config[key] = {"subject": subject_variables, "body": body_variables}
    return config
