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

import django.utils.timezone as tz

#from .exceptions import NotYourProfile,FailedUpateProfile
from .models import Event,Invitee, Invitation, Media, Album
#from .pagination import ProfilePagination
#from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer
from .serializers import EventCreateSerializer,EventSerializer,InviteSerializer,MyInvitesSerializer,InvitationSerializer,MediaSerializer
from .permissions import IsOwnerOrReadOnly, IsOwner, IsOwnerofInviteeObj, IsReceiverofInviteeObj,IsOwnerofInvitationObj,MediaViewer
from .exceptions import NotYourEvent,InviteeNotFound

User = get_user_model()


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
            print(data)
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
                    print(serializer.errors)
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
            print(e)
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
            print(invitee_id)
            rsvp_status = request.data['rsvp_status']
            inviter_id = event.creator
            print(inviter_id,'234569876543')
            invite_medium = "RSVP_code"
            if 'rsvp_message' in request.data:
                rsvp_message = request.data['rsvp_message']
            else:
                rsvp_message = " "
            max_guest_count = request.data['guest_count']
            guest_count = request.data['guest_count']
            rsvp_timestamp = tz.localtime()
            sent_timestamp = rsvp_timestamp
            print('11111234569876543')
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
                return Media.objects.filter(event = event, is_approved = True)
        else:
            return NotYourEvent


    def create(self, request, *args, **kwargs):
        #print('creating')
        eventcode = self.kwargs['slug']
        event = Event.objects.get(slug = eventcode)
        creator_user = request.user
        data = request.data
        data["poster"] = creator_user.pkid
        data["event"] = event.pkid
        #print(data)
        if 'image' in request.FILES:
            if request.FILES['image']:
                data["is_video"] = False
            else:
                data["is_video"] = True
        else:
            if request.FILES['video']:
                data["is_video"] = True

        
        serializer = self.serializer_class(data=data, context={"request": request})
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


