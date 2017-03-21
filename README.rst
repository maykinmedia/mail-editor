MailEditor
==========

[![Build Status](https://travis-ci.org/maykinmedia/mail_editor.svg?branch=master)](https://travis-ci.org/maykinmedia/mail_editor)
[![codecov](https://codecov.io/gh/maykinmedia/mail_editor/branch/master/graph/badge.svg)](https://codecov.io/gh/maykinmedia/mail_editor)
[![Lintly](https://lintly.com/gh/maykinmedia/mail_editor/badge.svg)](https://lintly.com/gh/maykinmedia/mail_editor/)

Django e-mail templates!

Many projects have a well defined set of events that trigger an outgoing e-mail,
and the sensible thing is to template these out.

However, doing code updates and deployments for small template tweaks are a bit
cumbersome and annoying.

This project aims to solve that - define the types of templates in the code,
and edit the actual templates in the front-end. Templates are validated on
syntax *and* required/optional content.

For e-mail sending and logging, we recommend using a solution such as `Django Yubin`_.

This is only tested on a postgres database.

Supported (read: Travis tested) are:

- python 2.7, 3.4, 3.5
- Django 1.8, 1.9, 1.10, 1.11
- PostgreSQL

Warning
-------

This project is currently in development and not stable.

Used NPM packages
-----------------

This package uses NPM. This is to inject the inline styles and minify the HTML

..code::shell

    npm install --save inline-css
    npm install --save htmlmin

Using the template
--------------------

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

    PACKAGE_JSON_DIR = '/path/to/the/package.json'
    ADD_BIN_PATH = True or False
    BIN_PATH = 'path/to/virtualenv/bin'

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

    CKEDITOR_CONFIGS = {
        'mail_editor': {
            'allowedContent': True,
            'height': 600,  # This is optional
        }
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
.. role:: python(code)
    :language: python
