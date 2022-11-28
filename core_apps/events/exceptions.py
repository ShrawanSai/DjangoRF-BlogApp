from rest_framework.exceptions import APIException

class NotYourEvent(APIException):
    status_code = 403
    default_detail = "You can't access this as the event doesn't belong to you!"

class InviteeNotFound(APIException):
    status_code = 403
    default_detail = "This event does not have the invitee record being seeked"

class NotYourMedia(APIException):
    status_code = 403
    default_detail = "You can't access this as the media doesn't belong to you!"

class NotYourAlbum(APIException):
    status_code = 403
    default_detail = "You can't access this as the album doesn't belong to you!"

class AlbumNotPartofEvent(APIException):
    status_code = 403
    default_detail = "This album does not belong to this event"

class MediaNotPartofEvent(APIException):
    status_code = 403
    default_detail = "This media does not belong to this event"

class AlbumNotAvailable(APIException):
    status_code = 403
    default_detail = "You can't access this album as it does not belong to you or it is not approved"

class NotYourWish(APIException):
    status_code = 403
    default_detail = "You can't access this as the wish doesn't belong to you!"

class WishNotPartofEvent(APIException):
    status_code = 403
    default_detail = "This wish does not belong to this event"