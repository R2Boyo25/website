# Generated by Django 5.0.7 on 2024-10-14 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kazani", "0003_remove_user_extra_seo_alter_user_about_me"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="about_me",
            field=models.TextField(blank=True, null=True),
        ),
    ]