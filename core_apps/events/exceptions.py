from rest_framework.exceptions import APIException

class NotYourEvent(APIException):
    status_code = 403
    default_detail = "You can't access this as the event doesn't belong to you!"

class InviteeNotFound(APIException):
    status_code = 403
    default_detail = "This event does not have the invitee record being seeked"