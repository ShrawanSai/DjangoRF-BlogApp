# Generated by Django 3.2.11 on 2022-10-15 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_profile_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='profile_photo',
            field=models.ImageField(default='/profile_default.png', upload_to='', verbose_name='profile photo'),
        ),
    ]