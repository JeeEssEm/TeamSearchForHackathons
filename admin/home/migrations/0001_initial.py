# Generated by Django 5.1.3 on 2024-11-25 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Invite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=100, verbose_name="Activation key"
                    ),
                ),
                ("is_used", models.BooleanField(default=False)),
            ],
        ),
    ]
