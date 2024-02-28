# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mail_editor", "0005_auto_20200220_1656"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailtemplate",
            name="base_template_path",
            field=models.CharField(
                default=b"",
                help_text=b"Leave empty for default template. Override to load a different template.",
                max_length=200,
                verbose_name="Base template path",
                blank=True,
            ),
        ),
    ]
