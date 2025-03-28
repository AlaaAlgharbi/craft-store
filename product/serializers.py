from email.mime import image
from rest_framework import serializers
from .models import CustomUser , Product , ProductAuction 

class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image","password"]
        extra_kwargs = {
            "password": {"write_only": True}}

class ProductSerializer(serializers.ModelSerializer):
    
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta :
        model = Product
        fields = ["name","price","category","image","description","user_name","user_image","rate"]
        read_only_fields  = ["user_image","user_name","rate"]
        extra_kwargs = {
            "category": {"write_only": True},
            "user": {"write_only": True},
            "description": {"write_only": True},}
        
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None


        
class ProductDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta : 
        model = Product
        fields = ["name","price","category","image","description",
                "user_name","user_image","rate","created_at"]
        read_only_fields = ["rate","created_at","user_name","user_image"]
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None 