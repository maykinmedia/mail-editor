from django.conf import settings
from django.core.management.base import BaseCommand

from ...helpers import find_template
from ...settings import get_choices


class Command(BaseCommand):
    help = "Create all new/missing templates (use this on every deploy)"

    def handle(self, *args, **options):
        choices = get_choices()
        for key, name in choices:
            if len(settings.LANGUAGES) > 1:
                for language_code, _language_name in settings.LANGUAGES:
                    find_template(key, language_code)
            else:
                find_template(key)
