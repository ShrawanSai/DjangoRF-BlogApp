# Generated by Django 3.2.11 on 2022-11-07 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0006_auto_20221107_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitee',
            name='guest_count',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invitee',
            name='invitee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invite_for', to=settings.AUTH_USER_MODEL),
        ),
    ]
