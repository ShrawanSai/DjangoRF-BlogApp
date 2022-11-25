from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinLengthValidator
from autoslug import AutoSlugField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
import datetime
from django.utils import timezone

from jsonfield import JSONField

from core_apps.common.models import TimeStampedUUIDModel

User = get_user_model()


class Event(TimeStampedUUIDModel):

    class EventType(models.TextChoices):
        BIRTHDAY = "birthday", _("birthday")
        WEDDING = "wedding", _("wedding")
        ANNIVERSARY = "anniversary", _("anniversary")
        FAREWELL = "farewell", _("farewell")
        OTHER = "other", _("other")


    title = models.CharField(verbose_name=_("event name"), max_length=100)
    eventcode = models.CharField(verbose_name=_("event code"), max_length=15,validators=[MinLengthValidator(5)])
    slug = AutoSlugField(populate_from="eventcode", always_update=True, unique=True)
    
    event_type = models.CharField(
        verbose_name=_("event_type"),
        choices=EventType.choices,
        default=EventType.OTHER,
        max_length=20,
    )

    location = models.TextField(max_length = 200)
    gmap_link = models.URLField(null = True, blank = True)

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "created_by"
    )

    hosts = models.ManyToManyField(User, related_name = "hosted_by")

    contact_person_name = models.CharField(max_length=50)
    contact_person_phonenumber = PhoneNumberField()

    banner_image = models.ImageField(
        verbose_name=_("banner image"),
        default="/profile_default.png"
    )

    start_timestamp = models.DateTimeField(null=True, blank = True)
    end_timestamp = models.DateTimeField(null=True, blank = True)
    created_timestamp = models.DateTimeField(auto_now_add = True)

    rsvp_code = models.CharField(max_length=7, validators=[MinLengthValidator(7)])

    has_website = models.BooleanField(default = True)
    has_gallery = models.BooleanField(default = True)
    has_schedule = models.BooleanField(default = False)
    has_wishes = models.BooleanField(default = False)

    others_field = JSONField(null=True, blank = True)

    def __str__(self):
        return f"{self.title} by {self.creator.get_full_name}"



class Invitee(TimeStampedUUIDModel):

    class RSVPresponse(models.TextChoices):
        NA = "N/A", _("N/A")
        YES = "yes", _("yes")
        NO = "no", _("no")

    class InviteMedium(models.TextChoices):
        WHATSAPP = "Whatsapp", _("Whatsapp")
        EMAIL = "Email", _("Email")
        RSVP_CODE = "RSVP_code", _("RSVP_code")
        UNKNOWN = "Unknown", _("Unknown")


    name = models.CharField(verbose_name=_("Invitee name"), max_length=100)
    invitee_phonenumber = PhoneNumberField()
    email = models.EmailField(verbose_name=_("Invitee email address"))
    invitee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "invite_for",
        null = True,
        blank = True,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name = "invite_event"
    )
    rsvp_status = models.CharField(
        verbose_name=_("RSVP response"),
        choices=RSVPresponse.choices,
        default=RSVPresponse.NA,
        max_length=5,
    )

    inviter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "invite_from"
    )

    invite_medium = models.CharField(
        verbose_name=_("Invite sent via"),
        choices=InviteMedium.choices,
        default=InviteMedium.UNKNOWN,
        max_length=15,
    )

    rsvp_message = models.TextField(max_length = 200)

    max_guest_count = models.PositiveSmallIntegerField(default = 1)

    guest_count = models.PositiveSmallIntegerField(null = True,blank = True)

    created_timestamp = models.DateTimeField(auto_now_add = True)
    sent_timestamp = models.DateTimeField(null = True,blank = True)
    rsvp_timestamp = models.DateTimeField(null = True,blank = True)

    others = JSONField(null=True, blank = True)

    def __str__(self):
        return f"{self.event}'s invite from {self.inviter} to {self.name}"
    
    def save(self, *args, **kwargs):
        if self.rsvp_status in ["yes","no"]:
            self.rsvp_timestamp = timezone.now()
        else:
            self.rsvp_timestamp = None
        super(Invitee, self).save(*args, **kwargs)

class Invitation(TimeStampedUUIDModel):

    event = models.OneToOneField(Event, related_name="event_of_invitation", on_delete=models.CASCADE)
    message = models.TextField(max_length = 300, null=True, blank = True)
    email_message = JSONField(null=True, blank = True)
    image = models.ImageField(
        verbose_name=_("Invitation image"),
        default="/profile_default.png",
        null=True, blank = True
    )
    others = JSONField(null=True, blank = True)

    def __str__(self):
        return f"{self.event}'s invitation"


class Album(TimeStampedUUIDModel):

    name = models.CharField(verbose_name=_("Album name"), max_length=100)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name = "album_of_event"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "creator_of_album"
    )
    created_timestamp = models.DateTimeField(auto_now_add = True)
    is_approved = models.BooleanField(default = False)
    file_count = models.PositiveSmallIntegerField(default = 0)
    download_count = models.PositiveSmallIntegerField(default = 0)


    thumbnail = models.ForeignKey(
        'Media',blank = True,
        on_delete=models.CASCADE,
        related_name = "thumbnail_of_album",
        null=True
    )

    album_metadata = JSONField(null=True, blank = True)
    others = JSONField(null=True, blank = True)

    def __str__(self):
        return f"{self.name} by {self.creator.first_name} | {self.event}"


class Media(TimeStampedUUIDModel):
    image = models.ImageField(
        verbose_name=_("Media image"),
        null=True, blank = True
    )
    video = models.FileField(
        verbose_name=_("Video File"),
        null=True, blank = True
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name = "media_event"
    )

    created_timestamp = models.DateTimeField(auto_now_add = True)
    is_approved = models.BooleanField(default = False)
    is_video = models.BooleanField(default = False)

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name = "album_of_media",
        null=True, 
        blank = True
    )

    poster = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = "media_uploadedby"
    )

    impressions = models.PositiveSmallIntegerField(default = 0)
    liked_by = models.ManyToManyField(User, related_name = "likers_of_media", blank = True)
    download_count = models.PositiveSmallIntegerField(default = 0)

    caption = models.CharField(verbose_name=_("Media Caption"), max_length=200,null=True, blank = True)

    file_metadata = JSONField(null=True, blank = True)
    others = JSONField(null=True, blank = True)

    def __str__(self):
        return f"{self.id} by {self.poster.first_name} | {self.event}"


