# Generated by Django 4.1 on 2022-08-07 17:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0007_remove_chat_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='channel_id',
            new_name='channel',
        ),
        migrations.RenameField(
            model_name='chat',
            old_name='chatter_id',
            new_name='chatter',
        ),
    ]
