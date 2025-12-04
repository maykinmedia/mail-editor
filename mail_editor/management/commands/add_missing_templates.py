from django.conf import settings
from django.core.management.base import BaseCommand

from ...helpers import find_template
from ...settings import get_choices


class Command(BaseCommand):
    help = "Create all new/missing templates (use this on every deploy)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain-id",
            type=int,
            default=None,
            help="Specify domain_id for the templates (defaults to MAIL_EDITOR_DEFAULT_DOMAIN_ID setting)",
        )

    def handle(self, *args, **options):
        domain_id = options.get("domain_id")
        choices = get_choices()
        for key, name in choices:
            if len(settings.LANGUAGES) > 1:
                for language_code, _language_name in settings.LANGUAGES:
                    find_template(key, language_code, domain_id=domain_id)
            else:
                find_template(key, domain_id=domain_id)
