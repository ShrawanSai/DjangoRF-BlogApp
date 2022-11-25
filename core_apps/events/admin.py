from django.contrib import admin

from .models import Event,Invitee,Invitation, Album, Media


class EventAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "title", "eventcode", "event_type", "creator", "created_timestamp"]
    list_filter = ["eventcode", "event_type", "creator"]
    list_display_links = ["id", "pkid"]


class InviteeAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "email", "invitee", "event", "inviter", "rsvp_status"]
    list_filter = ["event", "rsvp_status", "inviter","invitee"]
    list_display_links = ["id", "pkid"]


class InvitationAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "event"]
    list_filter = ["event"]
    list_display_links = ["id", "pkid"]


class AlbumAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "name","event","creator","is_approved","file_count","created_timestamp"]
    list_filter = ["event","creator","is_approved"]
    list_display_links = ["id", "pkid"]

class MediaAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id","event","poster","is_approved","is_video","album","created_timestamp"]
    list_filter = ["event","poster","is_approved"]
    list_display_links = ["id", "pkid"]



admin.site.register(Event, EventAdmin)
admin.site.register(Invitee, InviteeAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Media, MediaAdmin)