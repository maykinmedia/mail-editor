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

Installation
------------

Install with pip::

    pip install mail_editor


Add *'mail_editor'* to the installed apps::

    # settings.py

    INSTALLED_APPS = [
        ...
        'mail_editor',
        ...
    ]

.. _Django Yubin: https://github.com/APSL/django-yubin
.. _Sergei Maertens: https://github.com/sergei-maertens
.. _langerak-gkv: https://github.com/sergei-maertens/langerak-gkv/blob/master/src/langerak_gkv/mailing/mail_template.py
