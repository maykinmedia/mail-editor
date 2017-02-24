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
        for dict_variable in values.get('subject', []):
            subject_variables.append(Variable(dict_variable.get('variable'), required=dict_variable.get('required', True)))

        body_variables = []
        for dict_variable in values.get('body', []):
            body_variables.append(Variable(dict_variable.get('variable'), required=dict_variable.get('required', True)))

        config[key] = {
            'subject': subject_variables,
            'body': body_variables
        }
    return config
