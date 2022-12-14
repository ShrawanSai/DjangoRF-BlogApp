# Generated by Django 3.2.11 on 2022-11-23 08:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0014_alter_invitee_invite_medium'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('pkid', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Album name')),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('file_count', models.PositiveSmallIntegerField(default=0)),
                ('download_count', models.PositiveSmallIntegerField(default=0)),
                ('album_metadata', jsonfield.fields.JSONField(blank=True, null=True)),
                ('others', jsonfield.fields.JSONField(blank=True, null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_album', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_of_event', to='events.event')),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('pkid', models.BigAutoField(editable=False, primary_key=True, serialize=False)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, default='/profile_default.png', null=True, upload_to='', verbose_name='Media image')),
                ('video', models.FileField(blank=True, default='/profile_default.png', null=True, upload_to='', verbose_name='Video File')),
                ('created_timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_video', models.BooleanField(default=False)),
                ('impressions', models.PositiveSmallIntegerField(default=0)),
                ('download_count', models.PositiveSmallIntegerField(default=0)),
                ('caption', models.CharField(blank=True, max_length=200, null=True, verbose_name='Media Caption')),
                ('file_metadata', jsonfield.fields.JSONField(blank=True, null=True)),
                ('others', jsonfield.fields.JSONField(blank=True, null=True)),
                ('album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='album_of_media', to='events.album')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_event', to='events.event')),
                ('liked_by', models.ManyToManyField(related_name='likers_of_media', to=settings.AUTH_USER_MODEL)),
                ('poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_uploadedby', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='album',
            name='thumbnail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='thumbnail_of_album', to='events.media'),
        ),
    ]
