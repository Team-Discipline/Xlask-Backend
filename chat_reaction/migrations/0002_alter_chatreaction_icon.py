# Generated by Django 4.1.4 on 2023-01-21 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat_reaction", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatreaction",
            name="icon",
            field=models.CharField(max_length=20),
        ),
    ]
