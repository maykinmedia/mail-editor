MailEditor
==========

:Version: 0.3.9

|build-status| |code-quality| |black| |coverage|

|python-versions| |django-versions| |pypi-version|


Django e-mail templates!

Many projects have a well defined set of events that trigger an outgoing e-mail,
and the sensible thing is to template these out.

However, doing code updates and deployments for small template tweaks are a bit
cumbersome and annoying.

This project aims to solve that - define the types of templates in the code,
and edit the actual templates in the front-end. Templates are validated on
syntax *and* required/optional content.

This project also aims to solve the HTML email template problems that you can have when
supporting all email clients. This was also used by
`foundation for email`_. Foundation for email is a good way to build your initial email
template on development mode. It will generate a separate html file and css file.

For e-mail sending and logging, we recommend using a solution such as `Django Yubin`_.

This is only tested on a postgres database.

Supported are:

- python 3.11, 3.12, 3.13
- Django 4.2, 5.2
- PostgreSQL

Warning
-------

This project is currently in development and not stable.


Installation
------------

Install with pip:

.. code:: shell

    pip install mail_editor

Add *'mail_editor'* to the installed apps:

.. code:: python

    # settings.py

    INSTALLED_APPS = [
        ...
        'mail_editor',
        'ckeditor',
        ...
    ]

Add the urls:

.. code:: python

    # urls.py

    path('mail-editor/', include('mail_editor.urls', namespace='mail_editor')),


Using the template
--------------------

There are 2 templates that you can use.

The *_base.html*, this template can not be edited by the user. This will only be
rendered when the email is send.

The *_outer_table.html*, this template can be edited by the user and will be loaded
in the editor in the admin. This template will be saved in the database with the
modifications.

You can use the templates in some different ways. The shortest way is:

.. code:: python

    from mail_editor.helpers import find_template

    def email_stuff():
        template = find_template('activation')

        context = {
            'name': 'Test Person',
            'site_name': 'This site',
            'activation_link': 'https://github.com/maykinmedia/mail-editor',
        }

        template.send_email('test@example.com', context)

Settings
--------

The following settings are an example:

.. code:: python

    MAIL_EDITOR_CONF = {
        'activation': {
            'name': gettext_noop('Activation Email'),
            'description': gettext_noop('This email is used when people need to activate their account.'),
            'subject_default': 'Activeer uw account voor {{site_name}}',
            'body_default': """
                <h1>Hallo {{ name }},</h1>

                <p>Welkom! Je hebt je geregistreerd voor een {{ site_name }} account.</p>

                <p>{{ activation_link }}</p>
            """,
            'subject': [{
                'name': 'site_name',
                'description': gettext_noop('This is the name of the site. From the sites'),
                'example': gettext_noop('Example site'),
            }],
            'body': [{
                'name': 'name',
                'description': gettext_noop('This is the name of the user'),
                'example': gettext_noop('Jane Doe'),
            }, {
                'name': 'site_name',
                'description': gettext_noop('This is the name of the site. From the sites'),
                'example': gettext_noop('Example site'),
            }, {
                'name': 'activation_link',
                'description': gettext_noop('This is the link to activate their account.'),
                'example': gettext_noop('/'),
            }]
        },
        ...
    }

These settings are usefull to add:

.. code:: python

    # These settings make sure that CKEDITOR does not strip any html tags. like <center></center>
    CKEDITOR_CONFIGS = {
        'mail_editor': {
            'allowedContent': True,
            'contentsCss': ['/static/css/email.css'], # Enter the css file used to style the email.
            'height': 600,  # This is optional
            'entities': False, # This is added because CKEDITOR escapes the ' when you do an if statement
        }
    }

You can set template variables to all of the mail templates in the following fashion.

.. code:: python

    # static dictionary
    MAIL_EDITOR_BASE_CONTEXT = {
        'url': 'http://www.maykinmedia.nl',
    }

    # import path to callable that returns a dictionary
    MAIL_EDITOR_DYNAMIC_CONTEXT = "dotted.path.to.callable"


Installation
------------

Install with pip:

.. code:: shell

    pip install mail_editor


Local development
-----------------

To install and develop the library locally, use::

.. code-block:: bash

    pip install -e .[tests,coverage,release]

When running management commands via ``django-admin``, make sure to add the root
directory to the python path (or use ``python -m django <command>``):

.. code-block:: bash

    export PYTHONPATH=. DJANGO_SETTINGS_MODULE=testapp.settings
    django-admin check
    # or other commands like:
    django-admin migrate
    django-admin createsuperuser
    django-admin runserver
    # django-admin makemessages -l nl


.. _Django Yubin: https://github.com/APSL/django-yubin
.. _Sergei Maertens: https://github.com/sergei-maertens
.. _langerak-gkv: https://github.com/sergei-maertens/langerak-gkv/blob/master/src/langerak_gkv/mailing/mail_template.py
.. _foundation for email: http://foundation.zurb.com/emails.html
.. role:: python(code)
    :language: python

.. |build-status| image:: https://github.com/maykinmedia/mail-editor/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/mail-editor/actions?query=workflow%3A%22Run+CI%22

.. |code-quality| image:: https://github.com/maykinmedia/mail-editor/actions/workflows/code_quality.yml/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/mail-editor/actions?query=workflow%3A%22Code+quality+checks%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black

.. |coverage| image:: https://codecov.io/github/maykinmedia/mail-editor/graph/badge.svg?token=NXCPTBOL6N
    :target: https://codecov.io/gh/maykinmedia/mail-editor
    :alt: Coverage status


.. |python-versions| image:: https://img.shields.io/pypi/pyversions/mail-editor.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/mail-editor.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/mail-editor.svg
    :target: https://pypi.org/project/mail-editor/
