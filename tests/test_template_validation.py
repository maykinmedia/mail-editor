from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

from mail_editor.models import MailTemplate
from mail_editor.mail_template import validate_template


CONFIG = {
    'template': {
        'subject': [{
            'name': 'foo',
            'required': True,
        }],
        'body': [{
            'name': 'bar',
            'required': True,
        }],
    }
}


class TemplateValidationTests(TestCase):
    def test_valid_template(self):
        settings.MAIL_EDITOR_TEMPLATES = CONFIG.copy()
        template = MailTemplate(
            template_type='template',
            subject='{{ foo }}',
            body='{{ bar }}'
        )
        try:
            validate_template(template)
        except ValidationError:
            pytest.fail("Unexpected validationError")

    def test_template_syntax_error(self):
        settings.MAIL_EDITOR_TEMPLATES = CONFIG.copy()
        template = MailTemplate(
            template_type='template',
            subject='{{ foo bar }}',
            body='{{ bar }}'
        )
        with pytest.raises(ValidationError) as excinfo:
            validate_template(template)

        self.assertEqual(excinfo.value.code, 'syntax_error')

    def test_template_invalid_error(self):
        settings.MAIL_EDITOR_TEMPLATES = CONFIG.copy()
        template = MailTemplate(
            template_type='template',
            subject='{{ bar }}',
            body='{{ bar }}'
        )
        with pytest.raises(ValidationError) as excinfo:
            validate_template(template)

        self.assertEqual(excinfo.value.message, 'These variables are required, but missing: {{ foo }}')
