import os

SECRET_KEY = 'supersekrit'

DATABASES = {
    'default': {
        # Memory resident database, for easy testing.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'mail_editor',
]

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.path.pardir)
            )
        ],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]

MAIL_EDITOR_CONF = {
    'template': {
        'subject': [{
            'name': 'foo',
        }],
        'body': [{
            'name': 'bar',
        }],
    }
}
