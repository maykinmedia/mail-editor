from tempfile import TemporaryFile
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy as _

from mail_editor.helpers import find_template

CONFIG = {
    "test_template": {
        "name": _("test_template"),
        "description": _("Test description"),
        "subject_default": _("Important message for {{ id }}"),
        "body_default": _("Test mail sent from testcase with {{ id }}"),
        "subject": [{"name": "id", "description": ""}],
        "body": [{"name": "id", "description": "", "example": "321"}],
    }
}


def dynamic_context():
    return {"id": "DYNAMIC"}


class TemplateRenderTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

    def tearDown(self):
        patch.stopall()

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_simple(self):
        subject_context = {"id": "111"}
        body_context = {"id": "111"}

        template = find_template("test_template")

        subject, body = template.render(body_context, subj_context=subject_context)

        self.assertEqual(subject, "Important message for 111")
        self.assertIn("Test mail sent from testcase with 111", body)

    @override_settings(MAIL_EDITOR_CONF=CONFIG, MAIL_EDITOR_BASE_CONTEXT={"id": "BASE"})
    def test_base_context(self):
        subject_context = {}
        body_context = {}

        template = find_template("test_template")

        subject, body = template.render(body_context, subj_context=subject_context)

        self.assertEqual(subject, "Important message for BASE")
        self.assertIn("Test mail sent from testcase with BASE", body)

    @override_settings(
        MAIL_EDITOR_CONF=CONFIG,
        MAIL_EDITOR_DYNAMIC_CONTEXT="tests.test_template_rendering.dynamic_context",
    )
    def test_dynamic_context(self):
        subject_context = {}
        body_context = {}

        template = find_template("test_template")

        subject, body = template.render(body_context, subj_context=subject_context)

        self.assertEqual(subject, "Important message for DYNAMIC")
        self.assertIn("Test mail sent from testcase with DYNAMIC", body)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_incorrect_base_path(self):
        subject_context = {"id": "222"}
        body_context = {"id": "222"}

        template = find_template("test_template")
        template.base_template_path = b""

        subject, body = template.render(body_context, subj_context=subject_context)

        self.assertEqual(subject, "Important message for 222")
        self.assertIn("Test mail sent from testcase with 222", body)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_base_template_errors(self):
        subject_context = {"id": "333"}
        body_context = {"id": "333"}

        with TemporaryFile("w") as file:
            file.write("Template with errors {{ id }")
            file.seek(0)

            template = find_template("test_template")
            template.base_template_path = "__not-exists__"

            subject, body = template.render(body_context, subj_context=subject_context)

            self.assertEqual(subject, "Important message for 333")
            self.assertIn("Test mail sent from testcase with 333", body)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_render_preview(self):
        template = find_template("test_template")

        subject_context, body_context = template.get_preview_contexts()

        subject, body = template.render(body_context, subj_context=subject_context)

        # rendered placeholder
        self.assertEqual(subject, "Important message for --id--")
        # rendered example
        self.assertIn("Test mail sent from testcase with 321", body)
