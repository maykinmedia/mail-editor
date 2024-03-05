from base64 import b64encode
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy as _

from mail_editor.helpers import find_template
from mail_editor.process import FileData

CONFIG = {
    "test_template": {
        "name": _("test_template"),
        "description": _("Test description"),
        "subject_default": _("Important message for {{ id }}"),
        "body_default": _("Test mail sent from testcase with {{ id }}"),
        "subject": [{"name": "id", "description": ""}],
        "body": [{"name": "id", "description": ""}],
    },
    "process_template": {
        "name": _("test_template"),
        "description": _("Test description"),
        "subject_default": _("Important message for {{ id }}"),
        "body_default": '<img src="foo.jpg"><a href="foo">{{ id }}</a>',
        "subject": [{"name": "id", "description": ""}],
        "body": [{"name": "id", "description": ""}],
    },
}


class EmailSendTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

    def tearDown(self):
        patch.stopall()

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_send_email(self):
        subject_context = {"id": "111"}
        body_context = {"id": "111"}

        template = find_template("test_template")

        res = template.send_email(
            ["foo@example.com"], body_context, subj_context=subject_context
        )
        self.assertEqual(res, 1)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, _("Important message for 111"))
        self.assertIn(str(_("Test mail sent from testcase with 111")), message.body)
        self.assertEqual(message.attachments, [])

    @patch("mail_editor.process.cid_for_bytes", return_value="MY_CID", autospec=True)
    @patch(
        "mail_editor.process.load_image",
        return_value=FileData(b"abc", "image/jpg"),
        autospec=True,
    )
    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_send_email_processed_content(self, m0, m1):
        subject_context = {"id": "111"}
        body_context = {"id": "111"}

        template = find_template("process_template")

        res = template.send_email(
            ["foo@example.com"], body_context, subj_context=subject_context
        )
        self.assertEqual(res, 1)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, _("Important message for 111"))

        message_body, content_type = message.alternatives[0]
        self.assertEqual(content_type, "text/html")
        self.assertNotIn('<img src="foo.jpg">', message_body)
        self.assertIn('<img src="cid:MY_CID', message_body)

        self.assertNotIn('<a href="foo">', message_body)
        self.assertIn('<a href="http://testserver/foo"', message_body)

        self.assertEqual(len(message.attachments), 1)
        attach = message.attachments[0]

        self.assertEqual(attach["Content-ID"], "<MY_CID>")
        self.assertEqual(attach["Content-Type"], "image/jpg")
        payload = b64encode(b"abc").decode("utf8") + "\n"
        self.assertEqual(attach.get_payload(), payload)
