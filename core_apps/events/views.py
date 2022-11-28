from authors_api.settings.local import DEFAULT_FROM_EMAIL

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.db.models import Q
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser,FormParser

import django.utils.timezone as tz

#from .exceptions import NotYourProfile,FailedUpateProfile
from .models import Event,Invitee, Invitation, Media, Album, Wish
#from .pagination import ProfilePagination
#from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer
from .serializers import EventCreateSerializer,EventSerializer,InviteSerializer,MyInvitesSerializer,InvitationSerializer,MediaSerializer,AlbumSerializer, WishSerializer
from .permissions import IsOwnerOrReadOnly, IsOwner, IsOwnerofInviteeObj, IsReceiverofInviteeObj,IsOwnerofInvitationObj,MediaViewer,AlbumViewer
from .exceptions import NotYourEvent,InviteeNotFound, NotYourMedia, NotYourAlbum, AlbumNotAvailable, AlbumNotPartofEvent, MediaNotPartofEvent

User = get_user_model()


def check_if_user_invited(event,request):
    invited_or_owner = False
    if event.creator == request.user or request.user in event.hosts.all():
        invited_or_owner = True
    for i in Invitee.objects.filter(event = event):
        if i.invitee == request.user:
            invited_or_owner = True
            break
    if not invited_or_owner:
        raise NotYourEvent
    else:
        return True

def refresh_check_for_new_invites():
    invitee_records = Invitee.objects.all()
    for record in invitee_records:
        try:
            invitee_obj = User.objects.filter(Q(email = record.email) | Q(phone_number = record.invitee_phonenumber))[0]
            record.invitee = invitee_obj
            record.save()
        except Exception as e:
            pass



class EventCreateAPIView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = EventCreateSerializer
    #renderer_classes = [ArticleJSONRenderer]

    def create(self, request, *args, **kwargs):
        creator_user = request.user
        data = request.data
        data["creator"] = creator_user.pkid

        if 'hosts' in data.keys() and len(data['hosts']) > 0:
            host_emails = data["hosts"]
            x = []
            for email in host_emails:
                try:
                    x.append(User.objects.get(email = email).pkid)
                except User.DoesNotExist:
                    raise NotFound("A profile with this username does not exist")

            data["hosts"] = x
        else:
            data['hosts'] = [data["creator"]]

        
        serializer = self.serializer_class(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        '''logger.info(
            f"article {serializer.data.get('title')} created by {user.username}"
        )'''
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at", "username"]

    def get_queryset(self):
        queryset = Event.objects.filter(Q(creator = self.request.user) | Q(hosts = self.request.user))
        return queryset

class EventDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    #queryset = Event.objects.all()
    permission_classes = [
        permissions.IsAuthenticated, IsOwnerOrReadOnly
    ]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Event.objects.filter(Q(creator = self.request.user) | Q(hosts = self.request.user))
        return queryset

    def patch(self, request, *args, **kwargs):

        eventcode = self.kwargs['slug']
        obj = Event.objects.filter(eventcode = eventcode)[0]
        if obj.creator == request.user or request.user in obj.hosts.all():
            #creator_user = request.user
            data = request.data
            #data["creator"] = creator_user.pkid
            if 'hosts' in data.keys() and len(data['hosts']) > 0:
                #print('yess')
                host_emails = data["hosts"]
                x = []
                for email in host_emails:
                    try:
                        x.append(User.objects.get(email = email).pkid)
                    except User.DoesNotExist:
                        raise NotFound("A profile with this username does not exist")

                data["hosts"] = x
            else:
                data["hosts"] = []

            serializer = self.serializer_class(data=data, context={"request": request}, partial=True, instance = Event.objects.filter(slug = request.data["eventcode"])[0])
            serializer.is_valid(raise_exception=True)
            serializer.save(creator = request.user, hosts = data["hosts"])

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotYourEvent



class InviteeCreateAPIView(generics.CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwner
    ]
    serializer_class = InviteSerializer


    def create(self, request, *args, **kwargs):
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        if event.creator == self.request.user or self.request.user in event.hosts.all() :
            data = request.data
            for record in data:
                try:
                    invitee_obj = User.objects.filter(Q(email = record["email"]) | Q(phone_number = record["invitee_phonenumber"]))[0]
                    record["invitee"] = invitee_obj.pkid
                except Exception as e:
                    print(e)
                record["event"] = event.pkid
            #print(data)
            serializer = self.serializer_class(data=data, context={"request": request}, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(inviter=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise NotYourEvent
        


class InviteesforEventListAPIView(generics.ListAPIView):
    serializer_class = InviteSerializer
    permission_classes = [
        IsOwner,
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    lookup_field = "slug"

    def get_queryset(self):
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        if event.creator == self.request.user or self.request.user in event.hosts.all() :
            queryset = Invitee.objects.filter(event__eventcode = eventcode)
            return queryset
        else:
            raise NotYourEvent

class InviteeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InviteSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsOwnerofInviteeObj
    ]
    lookup_field = "id"


    def get_queryset(self):
        eventcode = self.kwargs['slug']
        queryset = Invitee.objects.filter(event__eventcode = eventcode)
        return queryset
    
    def patch(self, request, *args, **kwargs):
        try:
            eventcode = self.kwargs['slug']
            invitee_id = self.kwargs['id']
            event = Event.objects.get(slug = eventcode)
            invite_instance = Invitee.objects.get(id = invitee_id)
        except Exception as e:
            raise InviteeNotFound
        if invite_instance.event == event:
            if event.creator == self.request.user or self.request.user in event.hosts.all() :
                serializer = self.serializer_class(data=request.data, partial=True, instance = Invitee.objects.filter(id = invitee_id)[0])

                if not serializer.is_valid(raise_exception=True):
                    #print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                serializer.save(inviter=self.request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise NotYourEvent
        else:
            raise InviteeNotFound
        

class MyHostedEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at", "username"]

    def get_queryset(self):
        queryset = Event.objects.filter(Q(creator = self.request.user) | Q(hosts = self.request.user))
        return queryset

# @api_view(['PATCH'])
# @permission_classes((permissions.IsAuthenticated,))
# def send_invites(request,slug):
#     if request.method == 'PATCH':
#         event = Event.objects.get(slug = slug)
#         if event.creator == request.user or request.user in event.hosts.all():
#             data = request.data
#             for record in data:
#                 # Add send command here
#                 record["sent_timestamp"] = tz.localtime()
#             serializer = InviteSerializer(data = data, many=True, partial = True, instance = Invitee.objects.filter(id_in = data))
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             else:
#                 return Response(serializer.errors)
#         else:
#             raise NotYourEvent


class SendInvitesForMyEvent(APIView):

    def get_object(self, obj_id):
        try:
            return Invitee.objects.get(id=obj_id)
        except (Invitee.DoesNotExist):
            raise status.HTTP_400_BAD_REQUEST

    def validate_ids(self, id_list):
        for id in id_list:
            try:
                Invitee.objects.get(id=id)
            except (Invitee.DoesNotExist):
                raise status.HTTP_400_BAD_REQUEST
        return True

    def put(self, request, *args, **kwargs):

        eventcode = self.kwargs['slug']
        obj = Event.objects.filter(eventcode = eventcode)[0]
        if obj.creator == request.user or request.user in obj.hosts.all():
            id_list = request.data['ids']
            self.validate_ids(id_list=id_list)
            instances = []
            for id in id_list:
                obj = self.get_object(obj_id=id)
                obj.sent_timestamp = tz.localtime()
                obj.save()
                instances.append(obj)
            serializer = InviteSerializer(instances, many=True)
            return Response(serializer.data)
        else:
            raise NotYourEvent


class MyInvites(generics.ListAPIView):
    serializer_class = MyInvitesSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ["created_at", "username"]

    def get_queryset(self):
        refresh_check_for_new_invites()
        queryset = Invitee.objects.filter(invitee = self.request.user, sent_timestamp__isnull=False)
        return queryset


class MyInviteDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MyInvitesSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsReceiverofInviteeObj
    ]
    queryset = Invitee.objects.all()
    lookup_field = "id"


class InvitationDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerofInvitationObj
    ]
    queryset = Invitation.objects.all()
    lookup_field = "event__slug"


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def get_rsvps_list(request,slug):
    if request.method == 'POST':
        event = Event.objects.get(slug = slug)
        if event.creator == request.user or request.user in event.hosts.all():
            filter = request.data['filter']

            if int(filter) == 1:
                #Not RSVPd
                serializer = InviteSerializer(many=True, instance = Invitee.objects.filter(rsvp_timestamp__isnull=True, event = event, sent_timestamp__isnull=False))
            elif int(filter) == 2:
                #RSVPd
                serializer = InviteSerializer(many=True, instance = Invitee.objects.filter(rsvp_timestamp__isnull=False, event = event, sent_timestamp__isnull=False))
            elif int(filter) == 3:
                #RSVPd yes
                serializer = InviteSerializer(many=True, instance = Invitee.objects.filter(rsvp_timestamp__isnull=False, event = event, rsvp_status = "yes", sent_timestamp__isnull=False))
            elif int(filter) == 4:
                #RSVPd no
                serializer = InviteSerializer(many=True, instance = Invitee.objects.filter(rsvp_timestamp__isnull=False, event = event, rsvp_status = "no", sent_timestamp__isnull=False))
            else:
                #No filter
                serializer = InviteSerializer(many=True, instance = Invitee.objects.filter(event = event))
            
            return Response(serializer.data)
    
        else:
            raise NotYourEvent


@api_view(['POST','GET'])
@permission_classes((permissions.IsAuthenticated,))
def join_via_rsvp_code(request):
    
    if request.method == 'POST':
        try:
            event = Event.objects.filter(rsvp_code = request.data['rsvp_code'])[0]
        except Exception as e:
           
            raise NotFound("No event found")
        try:
            if 'name' in request.data:
                name = request.data['name']
            else:
                name = request.user.get_full_name

            if 'invitee_phonenumber' in request.data:
                invitee_phonenumber = request.data['invitee_phonenumber']
            else:
                invitee_phonenumber = str(request.user.phone_number)

            if 'email' in request.data:
                email = request.data['email']
            else:
                email = request.user.email    
            invitee_id = request.user.pkid
           
            rsvp_status = request.data['rsvp_status']
            inviter_id = event.creator
     
            invite_medium = "RSVP_code"
            if 'rsvp_message' in request.data:
                rsvp_message = request.data['rsvp_message']
            else:
                rsvp_message = " "
            max_guest_count = request.data['guest_count']
            guest_count = request.data['guest_count']
            rsvp_timestamp = tz.localtime()
            sent_timestamp = rsvp_timestamp
        
            data = {
                "name" : name,
                "invitee_phonenumber" : invitee_phonenumber,
                "email" : email,
                "invitee":invitee_id,
                "rsvp_status":rsvp_status,
                "inviter": inviter_id,
                "invite_medium":invite_medium,
                "rsvp_message":rsvp_message,
                "max_guest_count":max_guest_count,
                "guest_count":guest_count,
                "sent_timestamp":sent_timestamp,
                "rsvp_timestamp":rsvp_timestamp,
                "event":event.pkid
            }


            serializer = InviteSerializer(data=data, context={"request": request})
            if not serializer.is_valid(raise_exception=True):
                    return Response(serializer.errors)
            serializer.save(inviter = inviter_id)
            return Response(serializer.data)

        except Exception as e:
            raise NotFound(e)
    else:
        try:
            event = Event.objects.filter(rsvp_code = request.GET.get("rsvp_code"))[0]
        except Exception as e:
            raise NotFound("No event found")
        
        data = {
            "name":event.title,
            "event_type":event.event_type,
            "hosts":[e.get_full_name for e in event.hosts.all()],
            "invitation_image":event.event_of_invitation.image.url,
            "invitation_text":event.event_of_invitation.message
        }
        return Response(data, status=status.HTTP_200_OK)


################ Gallery #######################

class MediaCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,MediaViewer
    ]
    serializer_class = MediaSerializer

    def get_queryset(self):

        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)

        if event.creator == self.request.user or self.request.user in event.hosts.all():
            return Media.objects.filter(event = event)


        for i in Invitee.objects.filter(event = event):
            if i.invitee == self.request.user:
                return (Media.objects.filter(event = event, is_approved = True) | Media.objects.filter(event = event, poster = self.request.user)).distinct()
        else:
            raise NotYourEvent


    def create(self, request, *args, **kwargs):
        #print('creating')
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)


        if check_if_user_invited(event,self.request):
            creator_user = request.user
            data = request.data
            data["poster"] = creator_user.pkid
            data["event"] = event.pkid

            if "album" in data:
      
                album = Album.objects.get(id = data["album"])
                if album.is_approved or album.creator == self.request.user:
                    data["album"] = album.pkid
                    data["is_approved"] = album.is_approved
                else:
                    raise AlbumNotAvailable
            else:
                album = None


            if 'image' in request.FILES:
                if request.FILES['image']:
                    data["is_video"] = False
                else:
                    data["is_video"] = True
            elif 'video' in request.FILES:
                if request.FILES['video']:
                    data["is_video"] = True
                else:
                    data["is_video"] = False


            
            serializer = self.serializer_class(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise NotYourEvent

class MultipleMediaUploader(APIView):
    permission_classes = [
        permissions.IsAuthenticated,MediaViewer
    ]
    serializer_class = MediaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["poster__email"]

    def post(self, request, *args, **kwargs):
        
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)

        if check_if_user_invited(event,self.request):
            creator_user = request.user
            data = request.data
            #data["poster"] = creator_user.pkid
            #data["event"] = event.pkid
            sent_request = []
            if "album" in data:
        
                album = Album.objects.get(id = data["album"])
                #print(album)
                if album.is_approved or album.creator == self.request.user:
                    album_approval = album.is_approved
                    album = album.pkid
                    
                else:
                    raise AlbumNotAvailable
            else:
                album = None
                album_approval = None
            
            
            if 'image' in request.FILES:
                for record in request.FILES.getlist('image'):
                    sent_request.append({
                        "image":record,
                        "poster"  : creator_user.pkid,
                        "event" : event.pkid,
                        "is_video" : False,
                        "album" : album,
                        "is_approved" : album_approval

                    })


            elif 'video' in request.FILES:
                for record in request.FILES.getlist('video'):
                    sent_request.append({
                        "video":record,
                        "poster"  : creator_user.pkid,
                        "event" : event.pkid,
                        "is_video" : True,
                        "album" : album,
                        "is_approved" : album_approval

                    })
            else:
                return Response({"error":"invalid file type"}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.serializer_class(data=sent_request, many = True, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class MediaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MediaSerializer
    permission_classes = [
        permissions.IsAuthenticated, MediaViewer
    ]
    queryset = Media.objects.all()
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        media_id = self.kwargs['id']
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        media = Media.objects.get(id = media_id)

        if media.poster == self.request.user or event.creator == request.user or request.user in event.hosts.all():

            creator_user = request.user
            data = request.data
            data["poster"] = creator_user.pkid
            data["event"] = event.pkid

            if "album" in data:
                album = Album.objects.get(id = data["album"])
                if album.is_approved or album.creator == self.request.user:
                    data["album"] = album.pkid
                    data["is_approved"] = album.is_approved
                else:
                    raise AlbumNotAvailable


            if 'image' in request.FILES:
                if request.FILES['image']:
                    data["is_video"] = False
                else:
                    data["is_video"] = True
            elif 'video' in request.FILES:
                if request.FILES['video']:
                    data["is_video"] = True
                else:
                    data["is_video"] = False

            serializer = self.serializer_class(data=data, instance = Media.objects.get(id = media_id))
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotYourMedia



class AlbumCreateListAPIView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = AlbumSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["creator__email"]

    def get_queryset(self):

        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)

        if event.creator == self.request.user or self.request.user in event.hosts.all():
            return Album.objects.filter(event = event)

        for i in Invitee.objects.filter(event = event):
            if i.invitee == self.request.user:

                return (Album.objects.filter(event = event, is_approved = True) | Album.objects.filter(event = event, creator = self.request.user)).distinct()
        else:
            raise NotYourEvent


    def create(self, request, *args, **kwargs):
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        #print(event.creator)
        if check_if_user_invited(event,self.request):
            creator_user = request.user
            data = request.data
            data["creator"] = creator_user.pkid
            data["event"] = event.pkid

            if "thumbnail" in data:
                data["thumbnail"] = Media.objects.get(id = data["thumbnail"]).pkid
            serializer = self.serializer_class(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(creator = creator_user )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise NotYourEvent

class AlbumDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlbumSerializer
    permission_classes = [
        permissions.IsAuthenticated, AlbumViewer
    ]
    queryset = Album.objects.all()
    lookup_field = "id"

    def patch(self, request, *args, **kwargs):
        album_id = self.kwargs['id']
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        album = Album.objects.get(id = album_id)
        if album.creator == self.request.user or event.creator == request.user or request.user in event.hosts.all():
            creator_user = request.user
            data = request.data
            data["creator"] = creator_user.pkid
            data["event"] = event.pkid

            if "thumbnail" in data:
                try:
                    if data["thumbnail"] is not None:
                        data["thumbnail"] = Media.objects.get(id = data["thumbnail"]).pkid
                except Exception as e:
                    raise NotFound("That media id does not exist")

            if "is_approved" in data:
                medias = Media.objects.filter(album = album)
                for m in medias:
                    m.is_approved = data["is_approved"]
                    m.save()
            serializer = self.serializer_class(data=data,partial = True, instance = Album.objects.get(id = album_id))
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise NotYourAlbum

def get_album_object(obj_id):
    try:
        return Album.objects.get(id=obj_id)
    except (Album.DoesNotExist):
        raise status.HTTP_400_BAD_REQUEST

def get_media_object(obj_id):
    try:
        return Media.objects.get(id=obj_id)
    except (Media.DoesNotExist):
        raise status.HTTP_400_BAD_REQUEST


def validate_album_media_ids(id_list,event,album = True):
    if album:
        for id in id_list:
            try:
                album = Album.objects.get(id=id)
                if album.event != event:
                    raise AlbumNotPartofEvent
            except (Album.DoesNotExist):
                raise status.HTTP_400_BAD_REQUEST
        return True
    else:
        for id in id_list:
            try:
                media = Media.objects.get(id=id)
                if media.event != event:
                    raise MediaNotPartofEvent
            except (Media.DoesNotExist):
                raise status.HTTP_400_BAD_REQUEST
        return True



@api_view(['PATCH'])
@permission_classes((permissions.IsAuthenticated,))
def approve_an_item(request,slug):
    if request.method == 'PATCH':
        event = Event.objects.get(slug = slug)
        data = request.data
        if "is_approved" not in data:
            raise NotFound("New approval status not metioned")
        else:
            approval_status = data["is_approved"]

        if event.creator == request.user or request.user in event.hosts.all():
            album_serializer = None
            media_serializer = None
            if 'albums' in request.data:
                album_id_list = request.data['albums']
                validate_album_media_ids(id_list=album_id_list,event = event, album = True)
                instances = []
                for id in album_id_list:
                    obj = get_album_object(obj_id=id)
                    obj.is_approved = approval_status
                    medias = Media.objects.filter(album = obj)
                    for m in medias:
                        m.is_approved = approval_status
                        m.save()
                    obj.save()
                    instances.append(obj)
                album_serializer = AlbumSerializer(instances, many=True, partial = True)

            if 'medias' in request.data:
                medias_id_list = request.data['medias']
                validate_album_media_ids(id_list=medias_id_list, event = event ,album=False)
                instances = []
                for id in medias_id_list:
                    obj = get_media_object(obj_id=id)
                    obj.is_approved = approval_status
                    obj.save()
                    instances.append(obj)
                media_serializer = MediaSerializer(instances, many=True, partial = True)
            responses = {}
            if album_serializer:
                responses.update({'albums': album_serializer.data})
            if media_serializer:
                responses.update({'medias': media_serializer.data})
            return Response(responses, status=status.HTTP_200_OK)
        else:
            raise NotYourEvent
    

@api_view(['PATCH','GET'])
@permission_classes((permissions.IsAuthenticated,))
def like_media(request,slug,id):

    if request.method == 'GET':
        event = Event.objects.get(slug = slug)
        media = Media.objects.get(id = id)

        if check_if_user_invited(event,request):

            liked_by_user = False
            if request.user in media.liked_by.all():
                liked_by_user = True
            return Response({"user_like_status" : liked_by_user, "likes_count": len(media.liked_by.all()) ,"likers" : [user.get_full_name for user in media.liked_by.all()]},status=status.HTTP_200_OK)
        else:
            raise NotYourEvent



    if request.method == 'PATCH':
        event = Event.objects.get(slug = slug)
        media = Media.objects.get(id = id)
        like_status = request.data["like_status"]

        if check_if_user_invited(event,request):

            if not like_status:
                if request.user in media.liked_by.all():
                    media.liked_by.remove(request.user)
                    media.save()
                    return Response({"like_status" : f"{request.user.get_full_name} no longer likes this media object"}, status=status.HTTP_200_OK)
                else:
                    return Response({"like_status" : f"{request.user.get_full_name} does not like this media object"}, status=status.HTTP_200_OK)
            else:
                if request.user not in media.liked_by.all():
                    media.liked_by.add(request.user)
                    media.save()
                    return Response({"like_status" : f"{request.user.get_full_name} now likes this media"}, status=status.HTTP_200_OK)
                else:
                    return Response({"like_status" : f"{request.user.get_full_name} already likes this media object"}, status=status.HTTP_200_OK)
        else:
            raise NotYourEvent

@api_view(['PATCH','GET'])
@permission_classes((permissions.IsAuthenticated,))
def edit_carousel_list(request,slug):
    if request.method == 'PATCH':
        event = Event.objects.get(slug = slug)
        data = request.data
        if "is_carousel" not in data:
            raise NotFound("New carousel status not metioned")
        else:
            carousel_status = data["is_carousel"]

        if event.creator == request.user or request.user in event.hosts.all():
            if 'medias' in request.data:
                medias_id_list = request.data['medias']
                validate_album_media_ids(id_list=medias_id_list,event = event, album=False)
                for id in medias_id_list:
                    obj = get_media_object(obj_id=id)
                    obj.is_carousel = carousel_status
                    
                    if obj.is_carousel:
                        obj.is_approved = True
                    obj.save()
                return Response({"medias" : medias_id_list, "is_carousel" : carousel_status}, status=status.HTTP_200_OK)
            raise NotFound("Media list not metioned")
        raise NotYourEvent
    
    if request.method == 'GET':
        event = Event.objects.get(slug = slug)
        if check_if_user_invited(event,request):
            carousel_images = Media.objects.filter(is_carousel = True)
            return Response({"carousel_images" : [i.id for i in carousel_images], "carousel_count": len(carousel_images)},status=status.HTTP_200_OK)
        else:
            raise NotYourEvent

########## Wishes ####################

class WishCreateListAPIView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = WishSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["wisher__email"]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)

        if event.creator == self.request.user or self.request.user in event.hosts.all():
            return Wish.objects.filter(event = event)

        for i in Invitee.objects.filter(event = event):
            if i.invitee == self.request.user:
                return (Wish.objects.filter(event = event, is_approved = True) | Wish.objects.filter(event = event, wisher = self.request.user)).distinct()
        else:
            raise NotYourEvent

    def create(self, request, *args, **kwargs):
        #print('creating')
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        if check_if_user_invited(event,self.request):
            creator_user = request.user
            data = request.data
            data["wisher"] = creator_user.pkid
            data["event"] = event.pkid

            if 'wish_image' in request.FILES:
                if request.FILES['wish_image']:
                    data["is_video"] = False
                else:
                    data["is_video"] = None
            elif 'wish_video' in request.FILES:
                if request.FILES['wish_video']:
                    data["is_video"] = True
                else:
                    data["is_video"] = None
            else:
                data["is_video"] = None
            print(data)
            serializer = self.get_serializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save(event = event,wisher = creator_user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise NotYourEvent

    # def create(self, request, *args, **kwargs):
    #     eventcode = self.kwargs['slug']
    #     event = Event.objects.get(slug = eventcode)


    #     if check_if_user_invited(event,self.request):
    #         creator_user = request.user
    #         data = request.data
    #         data["wisher"] = creator_user.pkid
    #         data["event"] = event.pkid

    #         if 'wish_image' in request.FILES:
    #             if request.FILES['wish_image']:
    #                 data["is_video"] = False
    #                 data['wish_image'] = request.FILES['wish_image']
    #             else:
    #                 data["is_video"] = None
    #         elif 'wish_video' in request.FILES:
    #             if request.FILES['wish_video']:
    #                 data["is_video"] = True
    #             else:
    #                 data["is_video"] = None

    #         print(data)
    #         print(type(request.FILES['wish_image']))

    #         serializer = self.serializer_class(data=data, context={"request": request},  files = request.FILES.get('wish_image', None))
    #         if serializer.is_valid(raise_exception=True):
    #                 print(data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(event = event,wisher = creator_user)

    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         raise NotYourEvent