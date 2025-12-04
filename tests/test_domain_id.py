from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils.translation import gettext_lazy as _

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
    },
}


class DomainIdTestCase(TestCase):
    def setUp(self):
        site_patch = patch("mail_editor.helpers.get_current_site")
        current_site_mock = site_patch.start()
        current_site_mock.domain.return_value = "custom.domain.com"

    def tearDown(self):
        patch.stopall()

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_create_template_with_domain_id(self):
        """Test creating a template with a specific domain_id"""
        template = find_template("test_template", domain_id=2)
        self.assertEqual(template.domain_id, 2)
        self.assertEqual(template.template_type, "test_template")

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_create_template_default_domain_id(self):
        """Test creating a template with default domain_id"""
        template = find_template("test_template")
        self.assertEqual(template.domain_id, 1)

    @override_settings(MAIL_EDITOR_CONF=CONFIG, MAIL_EDITOR_DEFAULT_DOMAIN_ID=5)
    def test_create_template_custom_default_domain_id(self):
        """Test creating a template with custom default domain_id from settings"""
        template = find_template("test_template")
        self.assertEqual(template.domain_id, 5)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_multiple_templates_different_domains(self):
        """Test creating same template type for different domains"""
        template1 = find_template("test_template", domain_id=1)
        template2 = find_template("test_template", domain_id=2)

        self.assertNotEqual(template1.id, template2.id)
        self.assertEqual(template1.template_type, template2.template_type)
        self.assertEqual(template1.domain_id, 1)
        self.assertEqual(template2.domain_id, 2)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_template_with_language_and_domain(self):
        """Test creating templates with both language and domain_id"""
        template_en = find_template("test_template", language="en", domain_id=1)
        template_nl = find_template("test_template", language="nl", domain_id=1)
        template_en_domain2 = find_template("test_template", language="en", domain_id=2)

        self.assertEqual(template_en.language, "en")
        self.assertEqual(template_en.domain_id, 1)
        self.assertEqual(template_nl.language, "nl")
        self.assertEqual(template_nl.domain_id, 1)
        self.assertEqual(template_en_domain2.language, "en")
        self.assertEqual(template_en_domain2.domain_id, 2)

        # Ensure they are all different instances
        self.assertNotEqual(template_en.id, template_nl.id)
        self.assertNotEqual(template_en.id, template_en_domain2.id)
        self.assertNotEqual(template_nl.id, template_en_domain2.id)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_get_for_language_with_domain_id(self):
        """Test MailTemplateManager.get_for_language with domain_id"""
        # Create templates for different domains
        template1 = find_template("test_template", language="en", domain_id=1)
        template2 = find_template("test_template", language="en", domain_id=2)

        # Test retrieval with domain_id
        retrieved1 = MailTemplate.objects.get_for_language(
            "test_template", "en", domain_id=1
        )
        retrieved2 = MailTemplate.objects.get_for_language(
            "test_template", "en", domain_id=2
        )

        self.assertEqual(retrieved1.id, template1.id)
        self.assertEqual(retrieved2.id, template2.id)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_get_for_domain(self):
        """Test MailTemplateManager.get_for_domain method"""
        template = find_template("test_template", domain_id=3)

        retrieved = MailTemplate.objects.get_for_domain("test_template", domain_id=3)
        self.assertEqual(retrieved.id, template.id)
        self.assertEqual(retrieved.domain_id, 3)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_get_for_domain_with_language(self):
        """Test MailTemplateManager.get_for_domain with language parameter"""
        template_en = find_template("test_template", language="en", domain_id=3)
        template_default = find_template("test_template", domain_id=3)

        # Should return the language-specific template
        retrieved = MailTemplate.objects.get_for_domain(
            "test_template", domain_id=3, language="en"
        )
        self.assertEqual(retrieved.id, template_en.id)

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_unique_constraint_with_domain(self):
        """Test that templates are unique per type, language, and domain"""
        # Create first template
        template1 = find_template("test_template", language="en", domain_id=1)

        # Try to create duplicate (should return existing)
        template2 = find_template("test_template", language="en", domain_id=1)
        self.assertEqual(template1.id, template2.id)

        # Different domain should create new template
        template3 = find_template("test_template", language="en", domain_id=2)
        self.assertNotEqual(template1.id, template3.id)

    @override_settings(
        MAIL_EDITOR_CONF=CONFIG, MAIL_EDITOR_UNIQUE_LANGUAGE_TEMPLATES=True
    )
    def test_validation_unique_with_domain(self):
        """Test validation enforces uniqueness per domain"""
        # Create template
        template1 = MailTemplate.objects.create(
            template_type="test_template",
            language="en",
            domain_id=1,
            subject="Test",
            body="Body",
        )

        # Try to create duplicate manually
        template2 = MailTemplate(
            template_type="test_template",
            language="en",
            domain_id=1,
            subject="Test 2",
            body="Body 2",
        )

        with self.assertRaises(ValidationError) as cm:
            template2.full_clean()

        self.assertIn(
            "Mail template with this type, language and domain already exists",
            str(cm.exception),
        )

        # Different domain should be allowed
        template3 = MailTemplate(
            template_type="test_template",
            language="en",
            domain_id=2,
            subject="Test 3",
            body="Body 3",
        )
        template3.full_clean()  # Should not raise

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_send_email_with_domain(self):
        """Test sending email with domain-specific template"""
        template = find_template("test_template", domain_id=2)
        template.subject = "Domain 2 subject for {{ id }}"
        template.save()

        subject_context = {"id": "123"}
        body_context = {"id": "123"}

        message = template.build_message(
            ["test@example.com"], body_context, subj_context=subject_context
        )

        self.assertEqual(message.subject, "Domain 2 subject for 123")

    @override_settings(MAIL_EDITOR_CONF=CONFIG)
    def test_filter_templates_by_domain(self):
        """Test filtering templates by domain_id"""
        # Create templates for different domains
        find_template("test_template", domain_id=1)
        find_template("test_template", domain_id=2)
        find_template("test_template", domain_id=3)

        # Filter by domain
        domain1_templates = MailTemplate.objects.filter(domain_id=1)
        domain2_templates = MailTemplate.objects.filter(domain_id=2)

        self.assertEqual(domain1_templates.count(), 1)
        self.assertEqual(domain2_templates.count(), 1)
        self.assertEqual(domain1_templates.first().domain_id, 1)
        self.assertEqual(domain2_templates.first().domain_id, 2)
