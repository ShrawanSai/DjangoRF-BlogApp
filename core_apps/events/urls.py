from django.urls import path

from .views import (
    EventCreateAPIView, EventListAPIView,EventDetailAPIView, InviteesforEventListAPIView,
    InviteeCreateAPIView,InviteeDetailAPIView,MyHostedEventListAPIView,MyInvites, MyInviteDetailAPIView,
    SendInvitesForMyEvent,InvitationDetail, 
    get_rsvps_list,join_via_rsvp_code,
    MediaCreateAPIView, MultipleMediaUploader,  MediaDetailAPIView, AlbumCreateListAPIView, AlbumDetailAPIView, approve_an_item,
    like_media, edit_carousel_list,
    WishCreateListAPIView, WishDetailAPIView
)

urlpatterns = [
    path("create/", EventCreateAPIView.as_view(), name="create-new"),
    path("all/", EventListAPIView.as_view(), name="all-events"),
    path("eventid/<slug:slug>/", EventDetailAPIView.as_view(), name="event-detail"),
    path("eventid/<slug:slug>/invite/create/", InviteeCreateAPIView.as_view(), name="invitee-create"),
    path("eventid/<slug:slug>/all-invites/", InviteesforEventListAPIView.as_view(), name="invitees-for-event"),
    path("eventid/<slug:slug>/invite/<slug:id>/", InviteeDetailAPIView.as_view(), name="invitee-detail"),

    path("<slug:slug>/send_invites/",SendInvitesForMyEvent.as_view(), name = "send-invites"),
    path("<slug:slug>/view_rsvps/",get_rsvps_list, name = "rsvp-views"),

    path("my-hosted-events/",MyHostedEventListAPIView.as_view(),name="my-hosted-events"),
    path("my-invites/",MyInvites.as_view(),name="my-invites"),
    path("my-invite/<slug:id>/",MyInviteDetailAPIView.as_view(),name="my-invite-detail"),
    path("join-rsvp/",join_via_rsvp_code,name="rsvp-code-join"),

    path("eventid/<slug:event__slug>/invitation/", InvitationDetail.as_view(), name = "invitation-detail"),


    ## Gallery ####
    path("eventid/<slug:slug>/media/", MediaCreateAPIView.as_view(), name="media-list-create"),
    path("eventid/<slug:slug>/multiple-media-upload/", MultipleMediaUploader.as_view(), name="media-multiple-create"),
    path("eventid/<slug:slug>/media/<slug:id>/", MediaDetailAPIView.as_view(), name="media-detail"),

    path("eventid/<slug:slug>/album/", AlbumCreateListAPIView.as_view(), name="album-list-create"),
    path("eventid/<slug:slug>/album/<slug:id>/", AlbumDetailAPIView.as_view(), name="album-detail"),
    path("eventid/<slug:slug>/change-approval/", approve_an_item, name="change-approval-status"),

    path("eventid/<slug:slug>/like-media/<slug:id>/", like_media, name="like-media"),

    path("eventid/<slug:slug>/carousel-media/", edit_carousel_list, name="carousel-media"),

    ## Wishes ##

    path("eventid/<slug:slug>/wishes/", WishCreateListAPIView.as_view(), name="wish-list-create"),
    path("eventid/<slug:slug>/wishes/<slug:id>/", WishDetailAPIView.as_view(), name="wishes-detail"),

]

# {
#     "email":"saishrawan@yahoo.com",
#     "password":"pass1234567"
# }

# {
#     "email":"msaishrawan@gmail.com",
#     "password":"123123"
# }