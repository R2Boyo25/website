# Generated by Django 5.0.7 on 2024-08-05 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_article_is_homepage"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="no_container",
            field=models.BooleanField(default=False),
        ),
    ]
