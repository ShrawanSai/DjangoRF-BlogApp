from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = (
        "You are not allowed to update or delete an event that does not belong to you"
    )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.creator == request.user or request.user in obj.hosts.all()


class IsOwner(permissions.BasePermission):
    message = (
        "You do not have access to view this"
    )

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
       return obj.creator == request.user or request.user in obj.hosts.all()

class IsOwnerofInviteeObj(permissions.BasePermission):
    message = (
        "You do not have access to view this"
    )

    def has_object_permission(self, request, view, obj):
       return obj.event.creator == request.user or request.user in obj.event.hosts.all() 

class IsReceiverofInviteeObj(permissions.BasePermission):
    message = (
        "You do not have access to view this"
    )

    def has_object_permission(self, request, view, obj):
       return obj.invitee == request.user 

class IsOwnerofInvitationObj(permissions.BasePermission):
    message = (
        "You do not have access to CRUD this"
    )

    def has_object_permission(self, request, view, obj):
       return obj.event.creator == request.user or request.user in obj.event.hosts.all() 

class MediaViewer(permissions.BasePermission):
    message = (
        "You do not have access to View this Media"
    )

    def has_object_permission(self, request, view, obj):
        #print('im in')
        if obj.event.creator == request.user or request.user in obj.event.hosts.all():
            return True

        if obj.poster == request.user:
            return True
            
        if obj.event.invite_event.filter(invitee = request.user).exists():
            if obj.is_approved:
                if request.method in permissions.SAFE_METHODS:
                    return True
        
        return False

class AlbumViewer(permissions.BasePermission):
    message = (
        "You do not have access to View this Album"
    )

    def has_object_permission(self, request, view, obj):

        #print("This should be working")
        if obj.event.creator == request.user or request.user in obj.event.hosts.all():
            #print("This should not be working - 1")
            return True

        if obj.creator == request.user:
            #print("This should not be working - 2")
            return True
            
        if obj.event.invite_event.filter(invitee = request.user).exists():
            if obj.is_approved:
                if request.method in permissions.SAFE_METHODS:
                    return True
        #print("This should not be working")
        return False

class WishViewer(permissions.BasePermission):
    message = (
        "You do not have access to View this Wish"
    )

    def has_object_permission(self, request, view, obj):
        #print('im in')
        if obj.event.creator == request.user or request.user in obj.event.hosts.all():
            return True

        if obj.wisher == request.user:
            return True
            
        if obj.event.invite_event.filter(invitee = request.user).exists():
            if obj.is_approved:
                if request.method in permissions.SAFE_METHODS:
                    return True
        
        return False