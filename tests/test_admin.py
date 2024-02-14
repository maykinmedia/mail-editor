from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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


@override_settings(MAIL_EDITOR_CONF=CONFIG)
class AdminPreviewTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

        self.super_user = User.objects.create(username="admin", is_staff=True, is_superuser=True)

    def tearDown(self):
        patch.stopall()

    def test_changelist_view(self):
        template = find_template("test_template")

        url = reverse('admin:{}_{}_changelist'.format(template._meta.app_label, template._meta.model_name))

        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_change_view(self):
        template = find_template("test_template")

        url = reverse('admin:{}_{}_change'.format(template._meta.app_label, template._meta.model_name), args=[template.id])

        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_variable_view(self):
        template = find_template("test_template")

        url = reverse('admin:mailtemplate_variables', args=[template.template_type])

        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_preview_view(self):
        template = find_template("test_template")

        url = reverse('admin:mailtemplate_preview', args=[template.id])

        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, _("Important message for --id--"))

        # test sending the email
        self.client.post(url, {"recipient": "test@example.com"})

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, _("Important message for --id--"))
        self.assertIn(str(_("Test mail sent from testcase with --id--")), message.body)

    def test_render_view(self):
        template = find_template("test_template")

        url = reverse('admin:mailtemplate_render', args=[template.id])

        self.client.force_login(self.super_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, _("Test mail sent from testcase with --id--"))
