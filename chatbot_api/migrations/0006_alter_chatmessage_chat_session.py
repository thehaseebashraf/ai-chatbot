# Generated by Django 5.1.3 on 2024-12-03 12:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot_api", "0005_migrate_existing_messages"),
    ]

    operations = [
        migrations.AlterField(
            model_name="chatmessage",
            name="chat_session",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="chatbot_api.chatsession",
            ),
            preserve_default=False,
        ),
    ]