# Generated by Django 3.2.11 on 2022-11-07 19:32

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_auto_20221107_1939'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('pkid', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField(blank=True, max_length=300, null=True)),
                ('email_message', jsonfield.fields.JSONField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, default='/profile_default.png', null=True, upload_to='', verbose_name='Invitation image')),
                ('others', jsonfield.fields.JSONField(blank=True, null=True)),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event_of_invitation', to='events.event')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
    ]
