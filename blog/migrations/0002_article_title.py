# Generated by Django 5.0.7 on 2024-07-11 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="title",
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
