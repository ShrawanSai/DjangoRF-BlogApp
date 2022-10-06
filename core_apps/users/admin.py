from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import User


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = [
        "pkid",
        "id",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_staff",
        "is_active",
    ]
    list_display_links = ["id", "email","phone_number"]
    list_filter = ["email", "first_name", "last_name","phone_number", "is_staff"]
    fieldsets = (
        (
            _("Login Credentials"),
            {
                "fields": (
                    "email",
                    "phone_number",
                    "password",
                )
            },
        ),
        (
            _("Personal Information"),
            {"fields": ("first_name", "last_name")},
        ),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important Dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone_number", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ["email", "first_name", "last_name", "phone_number"]


admin.site.register(User, UserAdmin)