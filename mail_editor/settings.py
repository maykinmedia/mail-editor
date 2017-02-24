from django.conf import settings

from .mail_template import Variable


MAIL_EDITOR_CONF = getattr(settings, 'MAIL_EDITOR_CONF', None)


def get_choices():
    choices = [('', 'No choices are found.')]
    if MAIL_EDITOR_CONF:
        choices = []
        for key in MAIL_EDITOR_CONF:
            values = MAIL_EDITOR_CONF.get(key)
            choices += [(key, values.get('name'))]
    return choices


def get_config():
    config = {}
    if MAIL_EDITOR_CONF:
        for key in MAIL_EDITOR_CONF:
            values = MAIL_EDITOR_CONF.get(key)
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
