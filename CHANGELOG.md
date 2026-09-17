# Unreleased

**💥 Breaking changes**
- Dropped support for Python 3.10 and Django 3.2/4.2. Added support for Python 3.13 and Django 5.2/6.1.
- Removed `null=True` from `MailTemplate.language` and `MailTemplate.base_template_path`; both now default to
  `""` instead. A migration backfills any existing `NULL` values to `""`.
- Removed the deprecated `MAIL_EDITOR_TEMPLATES` setting fallback. Use `MAIL_EDITOR_CONF` instead.

# Version 0.1.0
- Added the basic functionality
