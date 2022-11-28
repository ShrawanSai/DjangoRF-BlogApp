from .models import Event,Invitee, Invitation, Media, Album, Wish
from rest_framework import serializers

class EventCreateSerializer(serializers.ModelSerializer):

    banner_image = serializers.SerializerMethodField()
    created_timestamp = serializers.SerializerMethodField()

    creator_info = serializers.SerializerMethodField(read_only=True)
    event_hosts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        exclude = ["pkid"]
    
    def get_created_timestamp(self, obj):
        now = obj.created_at
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_banner_image(self, obj):
        return obj.banner_image.url
    
    def get_event_hosts(self, obj):
        data = []
        for h in obj.hosts.all():
            data.append({
            "email": h.email,
            "fullname": h.get_full_name,
            })
        return data

    def get_creator_info(self, obj):
        return {
            "email": obj.creator.email,
            "fullname": obj.creator.get_full_name,
        }


class EventSerializer(serializers.ModelSerializer):

    banner_image = serializers.SerializerMethodField()
    created_timestamp = serializers.SerializerMethodField()
    invitation_whatsapp_message = serializers.CharField(source="event_of_invitation.message")
    invitation_email_message = serializers.CharField(source="event_of_invitation.email_message")
    invitation_image = serializers.SerializerMethodField()
    creator_info = serializers.SerializerMethodField(read_only=True)
    event_hosts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        exclude = ["pkid","hosts","creator"]
    
    def get_created_at(self, obj):
        now = obj.created_at
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_banner_image(self, obj):
        return obj.banner_image.url

    def get_invitation_image(self,obj):
        return obj.event_of_invitation.image.url

    def get_creator_info(self, obj):
        return {
            "email": obj.creator.email,
            "fullname": obj.creator.get_full_name,
        }

    def get_created_timestamp(self, obj):
        now = obj.created_at
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_event_hosts(self, obj):

        data = []
        for h in obj.hosts.all():
            data.append({
            "email": h.email,
            "fullname": h.get_full_name,
            })
        return data

class InviteSerializer(serializers.ModelSerializer):

    created_timestamp = serializers.SerializerMethodField()

    sent_timestamp_format = serializers.SerializerMethodField()
    rsvp_timestamp_format = serializers.SerializerMethodField()

    invitee_for_invite = serializers.SerializerMethodField(read_only=True)
    inviter = serializers.SerializerMethodField(read_only=True)
    event_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Invitee
        exclude = ["pkid"]
    
    def get_created_timestamp(self, obj):
        now = obj.created_timestamp
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_sent_timestamp_format(self, obj):
        if obj.sent_timestamp:
            now = obj.sent_timestamp
            formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
            return formatted_date
        else:
            return "Invite not sent yet"

    def get_rsvp_timestamp_format(self, obj):
        if obj.rsvp_timestamp:
            now = obj.rsvp_timestamp
            formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
            return formatted_date
        else:
            return "RSVP not sent yet"

    def get_invitee_for_invite(self,obj):
        if obj.invitee is None:
            return "Non Registered"
        else:
            return {"Invitee Name" : obj.invitee.get_full_name }

    def get_event_name(self,obj):
        return {
            "eventcode":obj.event.eventcode,
            "event name" : obj.event.title
        }

    def get_inviter(self,obj):
        return {"Inviter" : obj.inviter.get_full_name }

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['event'] = instance.event.eventcode
    
        return response


class MyInvitesSerializer(serializers.ModelSerializer):

    #created_timestamp = serializers.SerializerMethodField()

    sent_timestamp_format = serializers.SerializerMethodField()
    rsvp_timestamp_format = serializers.SerializerMethodField()

    invitee_details = serializers.SerializerMethodField(read_only=True)
    inviter_details = serializers.SerializerMethodField(read_only=True)
    event_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Invitee
        fields = [
        "id",
        "name",
        "invitee_phonenumber",
        "email",
        "rsvp_status",
        "invite_medium",
        "rsvp_message",
        "guest_count",
        "sent_timestamp_format",
        "rsvp_timestamp_format",
        "invitee_details",
        "inviter_details",
        "event_details"]

    def get_sent_timestamp_format(self, obj):
        if obj.sent_timestamp:
            now = obj.sent_timestamp
            formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
            return formatted_date
        else:
            return "Invite not sent yet"

    def get_rsvp_timestamp_format(self, obj):
        if obj.rsvp_timestamp:
            now = obj.rsvp_timestamp
            formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
            return formatted_date
        else:
            return "RSVP not sent yet"

    def get_invitee_details(self,obj):
        
        return {"Invitee Name" : obj.invitee.get_full_name }

    def get_event_details(self,obj):
        return {
            "eventcode":obj.event.eventcode,
            "event name" : obj.event.title,
            "event type" : obj.event.event_type,
            "hosts" : [user.get_full_name for user in obj.event.hosts.all()],
            "start date" : obj.event.start_timestamp
            }

    def get_inviter_details(self,obj):
        return {
            "Inviter" : obj.inviter.get_full_name
            }

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['event'] = instance.event.eventcode
    
        return response

class InvitationSerializer(serializers.ModelSerializer):

    invitation_photo = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        #fields = "__all__"
        exclude = ["pkid","event"]

    def get_invitation_photo(self, obj):
        return obj.image.url

class MediaSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField(read_only=True)
    album_details = serializers.SerializerMethodField(read_only=True)
    poster_info = serializers.SerializerMethodField(read_only=True)
    liked_by_list = serializers.SerializerMethodField()

    class Meta:
        model = Media
        exclude = ["pkid"]
    
    def get_created_at(self, obj):
        now = obj.created_timestamp
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_image_url(self, obj):
        if not obj.is_video:
            return obj.image.url
        else:
            return None

    def get_video_url(self, obj):
        if obj.is_video:
            return obj.video.url
        else:
            return None

    def get_album_details(self,obj):
        if obj.album:
            return {
                "albumid":obj.album.id,
                "album name" : obj.album.name,
                "album owner" : obj.album.creator.get_full_name,
                }
        else:
            return None

    def get_event_details(self,obj):
        return {
            "eventcode":obj.event.eventcode,
            "event name" : obj.event.title
            }

    def get_poster_info(self, obj):
        return {
            "email": obj.poster.email,
            "fullname": obj.poster.get_full_name,
        }

    def get_liked_by_list(self, obj):
        
        data = []
        for h in obj.liked_by.all():
            data.append({
            "email": h.email,
            "fullname": h.get_full_name,
            })
        return {"count": len(data), "liked_users" : data}


class AlbumSerializer(serializers.ModelSerializer):

    media = MediaSerializer(many=True, read_only=True, source = "album_of_media")

    thumbnail_image_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField(read_only=True)
    owner_info = serializers.SerializerMethodField(read_only=True)
    file_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Album
        fields = [
        "id",
        "name",
        "is_approved",
        "download_count",
        "thumbnail_image_url",
        "created_at",
        "event_details",
        "owner_info",
        "file_count",
        "media",
        "event",
        "album_metadata",
        "others"
        ]
        #exclude = ["pkid"]
    
    def get_created_at(self, obj):
        now = obj.created_timestamp
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_thumbnail_image_url(self, obj):
        if obj.thumbnail is not None:
            return obj.thumbnail.image.url
        else:
            return None

    def get_event_details(self,obj):
        return {
            "eventcode":obj.event.eventcode,
            "event name" : obj.event.title
            }

    def get_owner_info(self, obj):
        return {
            "email": obj.creator.email,
            "fullname": obj.creator.get_full_name,
        }

    def get_file_count(self, obj):
        return Media.objects.filter(album=obj).count()


class WishSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField(read_only=True)
    video_url = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField(read_only=True)
    wisher_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Wish
        fields = [
        "id",
        "wish_message",
        "wisher_info",
        "image_url",
        "video_url",
        "is_video",
        "created_at",
        "event_details",
        "is_approved",
        "others"
        ]
        #exclude = ["pkid"]
    
    def get_created_at(self, obj):
        now = obj.created_timestamp
        formatted_date = now.strftime("%m/%d/%Y, %H:%M:%S")
        return formatted_date

    def get_image_url(self, obj):
        if obj.is_video is None:
            return None
        if not obj.is_video:
            print('eririririririri')
            print(dir(obj))
            print(obj.wish_image)
            # all_fields = Wish._meta.get_fields()
            # #print([obj.i.name for i in all_fields])
            # print('_'*200)
           
            return obj.wish_image
        else:
            return None

    def get_video_url(self, obj):
        if obj.is_video is None:
            return None
        if obj.is_video:
            return obj.wish_video.url
        else:
            return None

    def get_event_details(self,obj):
        return {
            "eventcode":obj.event.eventcode,
            "event name" : obj.event.title
            }

    def get_wisher_info(self, obj):
        if obj.wish_by is not None:
            return {
                "wish_by": obj.wish_by,
                "user_fullname": obj.wisher.get_full_name,
                "user_email" : obj.wisher.email
                }
        else:
            return {
                "wish_by": obj.wisher.get_full_name,
                "user_email": obj.wisher.email,
                "user_fullname": obj.wisher.get_full_name
                }