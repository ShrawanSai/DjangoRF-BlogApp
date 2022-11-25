from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
import datetime
from jsonfield import JSONField

from core_apps.common.models import TimeStampedUUIDModel

User = get_user_model()


class Profile(TimeStampedUUIDModel):
    class Gender(models.TextChoices):
        MALE = "male", _("male")
        FEMALE = "female", _("female")
        OTHER = "other", _("other")

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    gender = models.CharField(
        verbose_name=_("gender"),
        choices=Gender.choices,
        default=Gender.OTHER,
        max_length=20,
    )
    country = CountryField(
        verbose_name=_("country"), default="IN", blank=False, null=False
    )
    city = models.CharField(
        verbose_name=_("city"),
        max_length=180,
        blank=False,
        null=False,
    )
    profile_photo = models.ImageField(
        verbose_name=_("profile photo"), default="/profile_default.png"
    )
    date_of_birth = models.DateField(max_length=8, null=True)

    #others_field = JSONField(null=True)

    """others_field = models.CharField(
        verbose_name=_("others"),
        max_length=180,
        blank=False,
        null=False,
    )"""

    def __str__(self):
        return f"{self.user.first_name}'s profile"

