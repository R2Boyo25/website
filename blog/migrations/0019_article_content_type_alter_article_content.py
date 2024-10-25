# Generated by Django 5.0.7 on 2024-10-14 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0018_article_override_seo"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="content_type",
            field=models.IntegerField(
                choices=[(1, "Json"), (2, "Markdown")], default=2
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="content",
            field=models.TextField(help_text="Content of the page"),
        ),
    ]
