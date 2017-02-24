from django.conf import settings


MAIL_EDITOR_CONF = getattr(settings, 'MAIL_EDITOR_CONF', None)
