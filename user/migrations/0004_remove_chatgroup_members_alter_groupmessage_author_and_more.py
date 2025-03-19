# Generated by Django 5.1.2 on 2025-01-31 04:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_chatgroup_avatar_chatgroup_members'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatgroup',
            name='members',
        ),
        migrations.AlterField(
            model_name='groupmessage',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.register'),
        ),
        migrations.AddField(
            model_name='chatgroup',
            name='members',
            field=models.ManyToManyField(to='user.register'),
        ),
    ]
