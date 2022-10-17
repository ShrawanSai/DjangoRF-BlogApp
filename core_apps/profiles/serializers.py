from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone_number = PhoneNumberField(source="user.phone_number")
    full_name = serializers.SerializerMethodField(read_only=True)
    profile_photo = serializers.SerializerMethodField()
    country = CountryField(name_only=True)
    #city = serializers.CharField()

    class Meta:
        model = Profile
        fields = [
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "id",
            "profile_photo",
            "gender",
            "country",
            "city",
            "date_of_birth",
        ]

    def get_full_name(self, obj):
        first_name = obj.user.first_name.title()
        last_name = obj.user.last_name.title()
        return f"{first_name} {last_name}"

    def get_profile_photo(self, obj):
        return obj.profile_photo.url


class UpdateProfileSerializer(serializers.ModelSerializer):
    country = CountryField(name_only=True)

    class Meta:
        model = Profile
        fields = [
            "date_of_birth",
            "profile_photo",
            "gender",
            "country",
            "city",
        ]


