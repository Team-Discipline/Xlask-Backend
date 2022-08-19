# Generated by Django 4.1 on 2022-08-12 13:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0008_rename_channel_id_chat_channel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='chatter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
