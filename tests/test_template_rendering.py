from tempfile import TemporaryFile

from django.conf import settings
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from mail_editor.models import MailTemplate
from mail_editor.helpers import find_template


try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


CONFIG = {
    "test_template": {
        "name": _("test_template"),
        "description": _("Test description"),
        "subject_default": _("Important message for {{ id }}"),
        "body_default": _("Test mail sent from testcase with {{ id }}"),
        "subject": [{"name": "id", "description": ""}],
        "body": [{"name": "id", "description": ""}],
    }
}


class TemplateRenderTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

    def tearDown(self):
        patch.stopall()

    def test_simple(self):
        settings.MAIL_EDITOR_CONF = CONFIG.copy()

        subject_context = {"id": "111"}
        body_context = {"id": "111"}

        template = find_template("test_template")

        subject, body = template.render(
            body_context, subj_context=subject_context
        )

        self.assertEquals(subject, "Important message for 111")
        self.assertIn("Test mail sent from testcase with 111", body)

    def test_incorrect_base_path(self):
        settings.MAIL_EDITOR_CONF = CONFIG.copy()

        subject_context = {"id": "222"}
        body_context = {"id": "222"}

        template = find_template("test_template")
        template.base_template_path = b''

        subject, body = template.render(
            body_context, subj_context=subject_context
        )

        self.assertEquals(subject, "Important message for 222")
        self.assertIn("Test mail sent from testcase with 222", body)

    def test_base_template_errors(self):
        settings.MAIL_EDITOR_CONF = CONFIG.copy()

        subject_context = {"id": "333"}
        body_context = {"id": "333"}

        with TemporaryFile("w") as file:
            file.write("Template with errors {{ id }")
            file.seek(0)

            template = find_template("test_template")
            template.base_template_path = file.name

            subject, body = template.render(
                body_context, subj_context=subject_context
            )

            self.assertEquals(subject, "Important message for 333")
            self.assertIn("Test mail sent from testcase with 333", body)
