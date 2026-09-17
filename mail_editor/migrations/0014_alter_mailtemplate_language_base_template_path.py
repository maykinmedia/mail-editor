from django.db import migrations, models


def backfill_null_values(apps, schema_editor):
    """
    Older rows may have NULL language/base_template_path values (the default
    before these fields stopped allowing NULL); replace them with the empty
    string, which is how "no value" is represented everywhere else these
    fields are queried.
    """
    MailTemplate = apps.get_model("mail_editor", "MailTemplate")
    MailTemplate.objects.filter(language__isnull=True).update(language="")
    MailTemplate.objects.filter(base_template_path__isnull=True).update(base_template_path="")


class Migration(migrations.Migration):

    dependencies = [
        ("mail_editor", "0013_alter_mailtemplate_language"),
    ]

    operations = [
        migrations.RunPython(backfill_null_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="mailtemplate",
            name="language",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.AlterField(
            model_name="mailtemplate",
            name="base_template_path",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Leave empty for default template. Override to load a different template.",
                max_length=200,
                verbose_name="Base template path",
            ),
        ),
    ]
