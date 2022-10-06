
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Authors API",
        default_version="v1",
        description="API endpoints for Shrawan's DRF project",
        contact=openapi.Contact(email="msaishrawan@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(settings.ADMIN_URL, admin.site.urls),

]


admin.site.site_header = "Shrawan's DRF project"
admin.site.site_title = "Shrawan's DRF project Admin Portal"
admin.site.index_title = "Welcome to the Shrawan's DRF project's API Portal"
