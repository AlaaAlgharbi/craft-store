from rest_framework import serializers
from .models import CustomUser , Product , ProductAuction , CustomUser

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

class ProductSerializer(serializers.ModelSerializer):
    class Meta :
        model = Product
        fields = ["name", "price", "created_at", "category", "image", "user" , "description"]

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta : 
        model = Product
        fields = ["name" , "price" , "rate" , "category"]
