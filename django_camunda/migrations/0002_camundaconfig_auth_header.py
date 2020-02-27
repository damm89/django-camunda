# Generated by Django 2.2.9 on 2020-01-13 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("django_camunda", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="camundaconfig",
            name="auth_header",
            field=models.TextField(
                blank=True,
                help_text="HTTP Authorization header value, required if the API is not open.",
                verbose_name="authorization header",
            ),
        )
    ]
