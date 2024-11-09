# Generated by Django 5.0.7 on 2024-11-06 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0021_alter_article_comments_enabled"),
    ]

    operations = [
        migrations.CreateModel(
            name="Upload",
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
                    "path",
                    models.CharField(
                        default="/media/",
                        help_text="Absolute path to serve file at (/media/image.png, etc.)",
                        max_length=512,
                    ),
                ),
                ("content", models.FileField(upload_to="uploads/")),
            ],
        ),
        migrations.AlterField(
            model_name="article",
            name="comments_enabled",
            field=models.BooleanField(
                default=True,
                help_text="Whether to display the form to submit comments and to display accepted comments.",
            ),
        ),
        migrations.AlterField(
            model_name="article",
            name="page_url",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="Absolute path to show page at (/ for homepage, /about, etc.)",
                max_length=512,
                null=True,
            ),
        ),
    ]
