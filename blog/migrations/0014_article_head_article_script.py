# Generated by Django 5.0.7 on 2024-08-06 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0013_rename_draft_article_is_draft_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="head",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="article",
            name="script",
            field=models.TextField(default=""),
        ),
    ]
