from django.core.exceptions import ValidationError

import pytest

from mail_editor.models import MailTemplate
from mail_editor.mail_template import validate_template


CONFIG = {
    'template': {
        'subject': [{
            'variable': 'foo',
            'required': True,
        }],
        'body': [{
            'variable': 'bar',
            'required': True,
        }],
    }
}


def test_valid_template(settings):
    settings.MAIL_EDITOR_CONF = CONFIG.copy()
    template = MailTemplate(
        template_type='template',
        subject='{{ foo }}',
        body='{{ bar }}'
    )
    try:
        validate_template(template)
    except ValidationError:
        pytest.fail("Unexpected validationError")


def test_template_syntax_error(settings):
    settings.MAIL_EDITOR_CONF = CONFIG.copy()
    template = MailTemplate(
        template_type='template',
        subject='{{ foo bar }}',
        body='{{ bar }}'
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_template(template)
    assert excinfo.value.error_code == 'syntax_error'
