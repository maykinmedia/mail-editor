import copy

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

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


class AdminPreviewTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

        self.super_user = User.objects.create(username="admin", is_staff=True, is_superuser=True)

    def tearDown(self):
        patch.stopall()

    def test_changelist_view(self):
        settings.MAIL_EDITOR_CONF = copy.deepcopy(CONFIG)

        template = find_template("test_template")

        url = reverse('admin:{}_{}_changelist'.format(template._meta.app_label, template._meta.model_name))

        self.client.force_login(self.super_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_change_view(self):
        settings.MAIL_EDITOR_CONF = copy.deepcopy(CONFIG)

        template = find_template("test_template")

        url = reverse('admin:{}_{}_change'.format(template._meta.app_label, template._meta.model_name), args=[template.id])

        self.client.force_login(self.super_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
