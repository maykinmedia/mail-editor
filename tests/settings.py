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
    "django.contrib.sessions",
    'django.contrib.messages',
    'django.contrib.admin',
    'mail_editor',
    "ckeditor",
]

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

ROOT_URLCONF = 'tests.urls'

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.path.pardir)
            )
        ],
        'APP_DIRS': True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
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

MAIL_EDITOR_BASE_HOST = "http://testserver"

SILENCED_SYSTEM_CHECKS = [
    "models.W042",  # AutoField warning not relevant for tests
]
