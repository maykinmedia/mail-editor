# Version 0.4.0 (Upcoming)

## Features
- Added `domain_id` field to `MailTemplate` model for multi-tenant support
- Updated `MailTemplateManager` with `get_for_language()` domain_id parameter
- Added new `MailTemplateManager.get_for_domain()` method for domain-specific template retrieval
- Updated `find_template()` helper to support domain_id parameter
- Added `MAIL_EDITOR_DEFAULT_DOMAIN_ID` setting (defaults to 1)
- Updated admin interface to display and filter by domain_id
- Updated `add_missing_templates` management command with `--domain-id` option
- Enhanced template uniqueness validation to include domain_id

## Migration
- Migration 0014: Added domain_id field with default value of 1

## Breaking Changes
- Templates are now unique per combination of type, language, and domain_id (previously type and language only)

# Version 0.1.0
- Added the basic functionality
