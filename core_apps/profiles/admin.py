from django.contrib import admin

from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["pkid", "id", "user", "gender", "country", "city", "date_of_birth"]
    list_filter = ["gender", "country", "city"]
    list_display_links = ["id", "pkid"]


admin.site.register(Profile, ProfileAdmin)