# Generated by Django 3.2.11 on 2022-11-03 20:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_profile_others_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='others_field',
        ),
    ]
