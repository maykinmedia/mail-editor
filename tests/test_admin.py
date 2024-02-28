from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_webtest import WebTest

from mail_editor.helpers import find_template
from mail_editor.models import MailTemplate

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
class AdminTestCase(WebTest):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()

        current_site_mock.domain.return_value = "custom.domain.com"

        self.super_user = User.objects.create(
            username="admin", is_staff=True, is_superuser=True
        )

    def tearDown(self):
        patch.stopall()

    def test_changelist_view(self):
        template = find_template("test_template")

        url = reverse("admin:mail_editor_mailtemplate_changelist")

        response = self.app.get(url, user=self.super_user)

        # test search isn't broken
        form = response.forms["changelist-search"]
        form["q"] = "test"
        response = form.submit()
        self.assertEqual([template], list(response.context["cl"].queryset.all()))

        form = response.forms["changelist-search"]
        form["q"] = "not_found"
        response = form.submit()
        self.assertEqual([], list(response.context["cl"].queryset.all()))

    def test_changelist_view__reset_template_action(self):
        template = find_template("test_template")
        template.body = "something else"
        template.subject = "something else"
        template.save()

        url = reverse("admin:mail_editor_mailtemplate_changelist")

        response = self.app.get(url, user=self.super_user)
        form = response.forms["changelist-form"]
        form["action"] = "reload_templates"
        form["_selected_action"] = [str(template.pk)]
        response = form.submit().follow()

        template.refresh_from_db()
        self.assertIn(
            str(_("Test mail sent from testcase with {{ id }}")),
            template.body,
        )
        self.assertEqual(template.subject, _("Important message for {{ id }}"))

    def test_change_view(self):
        template = find_template("test_template")

        url = reverse("admin:mail_editor_mailtemplate_change", args=[template.id])

        response = self.app.get(url, user=self.super_user)
        form = response.forms["mailtemplate_form"]
        form["subject"] = "mail subject"
        form.submit()
        template.refresh_from_db()
        self.assertEqual(template.subject, "mail subject")

    def test_add_view(self):
        url = reverse("admin:mail_editor_mailtemplate_add")

        response = self.app.get(url, user=self.super_user)
        form = response.forms["mailtemplate_form"]
        form["template_type"] = "test_template"
        form["subject"] = "mail subject"
        form["body"] = "mail body"
        response = form.submit().follow()

        template = MailTemplate.objects.get()
        self.assertEqual(template.template_type, "test_template")
        self.assertEqual(template.subject, "mail subject")
        self.assertEqual(template.body, "mail body")

    def test_add_view__handle_duplicates(self):
        template = find_template("test_template")

        url = reverse("admin:mail_editor_mailtemplate_add")

        with self.subTest("unique language templates"):
            with override_settings(MAIL_EDITOR_UNIQUE_LANGUAGE_TEMPLATES=True):
                response = self.app.get(url, user=self.super_user)
                form = response.forms["mailtemplate_form"]
                form["template_type"] = "test_template"
                form["subject"] = "mail subject"
                form["body"] = "mail body"
                response = form.submit(status=200)
                self.assertEqual(
                    str(response.context["errors"][0][0]),
                    _("Mail template with this type and language already exists"),
                )

                self.assertEqual(
                    1,
                    MailTemplate.objects.filter(template_type="test_template").count(),
                )

        with self.subTest("not-unique language templates"):
            with override_settings(MAIL_EDITOR_UNIQUE_LANGUAGE_TEMPLATES=False):
                response = self.app.get(url, user=self.super_user)
                form = response.forms["mailtemplate_form"]
                form["template_type"] = "test_template"
                form["subject"] = "mail subject"
                form["body"] = "mail body"
                response = form.submit().follow()
                self.assertEqual(
                    2,
                    MailTemplate.objects.filter(template_type="test_template").count(),
                )

    def test_variable_view(self):
        template = find_template("test_template")

        url = reverse("admin:mailtemplate_variables", args=[template.template_type])

        response = self.app.get(url, user=self.super_user)

    def test_preview_view(self):
        template = find_template("test_template")

        url = reverse("admin:mailtemplate_preview", args=[template.id])

        response = self.app.get(url, user=self.super_user)

        self.assertContains(response, _("Important message for --id--"))

        # send the mail
        form = response.forms["mailtemplate_form"]
        form["recipient"] = "test@example.com"
        response = form.submit()

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, _("Important message for --id--"))
        self.assertIn(str(_("Test mail sent from testcase with --id--")), message.body)

    def test_render_view(self):
        template = find_template("test_template")

        url = reverse("admin:mailtemplate_render", args=[template.id])

        response = self.app.get(url, user=self.super_user)

        self.assertIn(str(_("Test mail sent from testcase with --id--")), response.text)
