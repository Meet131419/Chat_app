# Generated by Django 5.1.2 on 2025-01-27 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_chatgroup_groupmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatgroup',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='chat_group_avatars/'),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='members',
            field=models.CharField(default=1, max_length=255),
        ),
    ]
