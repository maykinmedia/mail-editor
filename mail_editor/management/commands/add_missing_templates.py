from django.core.management.base import BaseCommand

from mail_editor import find_template
from mail_editor.settings import get_choices


class Command(BaseCommand):
    help = "Create all new/missing templates (use this on every deploy)"

    def handle(self, *args, **options):
        choices = get_choices()
        for key, name in choices:
            find_template(key)
