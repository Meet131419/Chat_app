# Generated by Django 5.1.2 on 2025-03-12 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_groupmessage_created_delete_fcmtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmessage',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
