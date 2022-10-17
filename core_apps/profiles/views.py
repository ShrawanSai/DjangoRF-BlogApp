from authors_api.settings.local import DEFAULT_FROM_EMAIL

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import NotYourProfile
from .models import Profile
from .pagination import ProfilePagination
from .renderers import ProfileJSONRenderer, ProfilesJSONRenderer
from .serializers import ProfileSerializer, UpdateProfileSerializer

User = get_user_model()

# @api_view(["GET"])
# @permission_classes([permissions.AllowAny])
# def get_all_profiles(request):
#     profiles = Profile.objects.all()
#     serializer = ProfileSerializer(profiles, many=True)
#     namespaced_response = {"profiles": serializer.data}
#     return Response(namespaced_response, status=status.HTTP_200_OK)

# @api_view(["GET"])
# @permission_classes([permissions.AllowAny])
# def get_profile_details(request,username):
#     try:
#         user_profile = Profile.objects.get(user__username=username)
#     except Profile.DoesNotExist:
#         raise NotFound('A profile with this username does not exist...')

#     serializer = ProfileSerializer(user_profile, many=False)
#     formatted_response = {"profile": serializer.data}
#     return Response (formatted_response, status=status.HTTP_200_OK)

class ProfileListAPIView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.all()
    renderer_classes = (ProfilesJSONRenderer,)
    pagination_class = ProfilePagination

class ProfileDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer,)

    def retrieve(self, request, email, *args, **kwargs):
        try:
            profile = self.queryset.get(user__email=email)
        except Profile.DoesNotExist:
            raise NotFound("A profile with this username does not exist")

        serializer = self.serializer_class(profile, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Profile.objects.select_related("user")
    renderer_classes = [ProfileJSONRenderer]
    serializer_class = UpdateProfileSerializer

    def patch(self, request, email):
        try:
            self.queryset.get(user__email=email)
        except Profile.DoesNotExist:
            raise NotFound("A profile with this email does not exist")

        user_name = request.user.email
        if user_name != email:
            raise NotYourProfile

        data = request.data
        serializer = UpdateProfileSerializer(
            instance=request.user.profile, data=data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)