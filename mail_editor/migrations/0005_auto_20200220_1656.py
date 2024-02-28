# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mail_editor", "0004_auto_20170406_1814"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mailtemplate",
            name="language",
            field=models.CharField(
                blank=True,
                max_length=10,
                null=True,
                choices=[(b"nl", "Netherlands"), (b"en", "English")],
            ),
        ),
    ]
