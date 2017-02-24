MailEditor
==========

[![Build Status](https://travis-ci.org/maykinmedia/mail_editor.svg?branch=master)](https://travis-ci.org/maykinmedia/mail_editor)
[![codecov](https://codecov.io/gh/maykinmedia/mail_editor/branch/master/graph/badge.svg)](https://codecov.io/gh/maykinmedia/mail_editor)
[![Lintly](https://lintly.com/gh/maykinmedia/mail_editor/badge.svg)](https://lintly.com/gh/maykinmedia/mail_editor/)

This project is used for creating and editing email templates. If you want the logging of the email templates please use `Django Yubin`_.

This code is based on code from a project from `Sergei Maertens`_ -> `langerak-gkv`_

This is only tested on a postgres database.

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
