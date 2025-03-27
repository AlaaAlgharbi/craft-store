from rest_framework import serializers
from .models import CustomUser

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image"]

class SianUpUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image","password"]

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image"]
