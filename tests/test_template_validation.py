from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

from mail_editor.models import MailTemplate
from mail_editor.mail_template import validate_template
from . import settings


class TemplateValidationTests(TestCase):
    def test_valid_template(self):
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
        template = MailTemplate(
            template_type='template',
            subject='{{ foo bar }}',
            body='{{ bar }}'
        )
        with pytest.raises(ValidationError) as excinfo:
            validate_template(template)

        self.assertEqual(excinfo.value.code, 'syntax_error')

    def test_template_invalid_error(self):
        template = MailTemplate(
            template_type='template',
            subject='{{ bar }}',
            body='{{ bar }}'
        )

        template.CONFIG["template"]["subject"][0].required = True
        with pytest.raises(ValidationError) as excinfo:
            validate_template(template)

        self.assertEqual(excinfo.value.message, 'These variables are required, but missing: {{ foo }}')

    def test_valid_template_with_attribute(self):
        template = MailTemplate(
            template_type='template',
            subject='{{ foo.bar }}',
            body='{{ bar.foo }}'
        )
        try:
            validate_template(template)
        except ValidationError:
            pytest.fail("Unexpected validationError")

    def test_valid_template_with_attribute_required_variable(self):
        template = MailTemplate(
            template_type='template',
            subject='{{ foo.bar }}',
            body='{{ bar.foo }}'
        )

        # Make foo required
        template.CONFIG["template"]["subject"][0].required = True
        try:
            validate_template(template)
        except ValidationError:
            pytest.fail("Unexpected validationError")
