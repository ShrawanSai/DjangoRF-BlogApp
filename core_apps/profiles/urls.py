from django.urls import path

from .views import (
    ProfileDetailAPIView,
    ProfileListAPIView,
    UpdateProfileAPIView,
)

urlpatterns = [
    path("all/", ProfileListAPIView.as_view(), name="all-profiles"),
    path(
        "user/<str:email>/", ProfileDetailAPIView.as_view(), name="profile-details"
    ),
    path(
        "update/<str:email>/", UpdateProfileAPIView.as_view(), name="profile-update"
    ),
]