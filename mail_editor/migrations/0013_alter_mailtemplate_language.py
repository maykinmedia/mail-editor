# Generated by Django 3.2.15 on 2023-04-13 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail_editor', '0012_auto_20230102_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailtemplate',
            name='language',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]