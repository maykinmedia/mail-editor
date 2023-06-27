MailEditor
==========

.. image:: https://travis-ci.org/maykinmedia/mail-editor.svg?branch=master
    :target: https://travis-ci.org/maykinmedia/mail-editor
    :alt: Travis
.. image:: https://codecov.io/gh/maykinmedia/mail-editor/branch/develop/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/mail-editor
    :alt: Coverage
.. image:: https://lintly.com/gh/maykinmedia/mail-editor/badge.svg
    :target: https://lintly.com/gh/maykinmedia/mail-editor/
    :alt: Lintly
.. image:: https://bettercodehub.com/edge/badge/maykinmedia/mail-editor?branch=master
    :target: https://bettercodehub.com/results/maykinmedia/mail-editor
    :alt: BCH compliance
.. image:: https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg
   :target: https://codeclimate.com/github/codeclimate/codeclimate
   :alt: Code Climate


Django e-mail templates!

Many projects have a well defined set of events that trigger an outgoing e-mail,
and the sensible thing is to template these out.

However, doing code updates and deployments for small template tweaks are a bit
cumbersome and annoying.

This project aims to solve that - define the types of templates in the code,
and edit the actual templates in the front-end. Templates are validated on
syntax *and* required/optional content.

This project also aims to solve the HTML email template problems that you can have when
supporting all email clients. For this we will inject the css as inline styles.
We do this using a node project calles inline-css. This was also used by
`foundation for email`_. Foundation for email is a good way to build your initial email
template on development mode. It will generate a separete html file and css file.

For e-mail sending and logging, we recommend using a solution such as `Django Yubin`_.

This is only tested on a postgres database.

Supported (read: tested in CI) are:

- Python: |python-versions|
- Django: |django-versions|
- PostgreSQL

Warning
-------

This project is currently in development and not stable.

Used NPM packages
-----------------

This package uses NPM. This is to inject the inline styles and minify the HTML.
This packages are needed to make the email complient for all the email clients.

.. code:: shell

    npm install --save inline-css
    npm install --save html-minifier


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

    url(r'^mail-editor/', include('mail_editor.urls', namespace='mail_editor')),


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

The following settings are mandatory:

.. code:: python

    MAIL_EDITOR_CONF = {
        'activation': {
            'name': ugettext_noop('Activation Email'),
            'description': ugettext_noop('This email is used when people need to activate their account.'),
            'subject_default': 'Activeer uw account voor {{site_name}}',
            'body_default': """
                <h1>Hallo {{ name }},</h1>

                <p>Welkom! Je hebt je geregistreerd voor een {{ site_name }} account.</p>

                <p>{{ activation_link }}</p>
            """,
            'subject': [{
                'name': 'site_name',
                'description': ugettext_noop('This is the name of the site. From the sites'),
            }],
            'body': [{
                'name': 'name',
                'description': ugettext_noop('This is the name of the user'),
            }, {
                'name': 'site_name',
                'description': ugettext_noop('This is the name of the site. From the sites'),
            }, {
                'name': 'activation_link',
                'description': ugettext_noop('This is the link to activate their account.'),
            }]
        },
        ...
    }

These settings are usefull to add:

.. code:: python

    # These settings are for inlining the css.
    MAIL_EDITOR_PACKAGE_JSON_DIR = '/path/to/the/package.json'
    MAIL_EDITOR_ADD_BIN_PATH = True or False
    MAIL_EDITOR_BIN_PATH = 'path/to/virtualenv/bin'

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

MAIL_EDITOR_BASE_CONTEXT = {
    'url': 'http://www.maykinmedia.nl',
}


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
        ...
    ]

.. _Django Yubin: https://github.com/APSL/django-yubin
.. _Sergei Maertens: https://github.com/sergei-maertens
.. _langerak-gkv: https://github.com/sergei-maertens/langerak-gkv/blob/master/src/langerak_gkv/mailing/mail_template.py
.. _foundation for email: http://foundation.zurb.com/emails.html
.. role:: python(code)
    :language: python

.. |build-status| image:: https://github.com/maykinmedia/mail-editor/workflows/Run%20CI/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/mail-editor/actions?query=workflow%3A%22Run+CI%22

.. |code-quality| image:: https://github.com/maykinmedia/mail-editor/workflows/Code%20quality%20checks/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/mail-editor/actions?query=workflow%3A%22Code+quality+checks%22

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |coverage| image:: https://codecov.io/gh/maykinmedia/mail-editor/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/mail-editor
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/mail-editor/badge/?version=latest
    :target: https://mail-editor.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/mail-editor.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/mail-editor.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/mail-editor.svg
    :target: https://pypi.org/project/mail-editor/
