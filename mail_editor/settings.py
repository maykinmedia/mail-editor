from django.conf import settings

from .mail_template import Variable


def get_choices():
    choices = []
    for key, values in settings.MAIL_EDITOR_CONF.items():
        choices += [(key, values.get('name'))]
    return choices


def get_config():
    config = {}
    for key, values in settings.MAIL_EDITOR_CONF.items():
        subject_variables = []
        for var in values.get('subject', []):
            subject_variables.append(Variable(**var))

        body_variables = []
        for var in values.get('body', []):
            body_variables.append(Variable(**var))

        config[key] = {
            'subject': subject_variables,
            'body': body_variables
        }
    return config
