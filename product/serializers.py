from email.mime import image
from rest_framework import serializers
from .models import CustomUser , Product , ProductAuction 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image","password"]
        extra_kwargs = {
            "password": {"write_only": True}}
        
    def create(self, validated_data):
        # استدعاء set_password لتشفير كلمة المرور
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # تحديث الحقول مع التحقق من كلمة المرور الجديدة
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
class ProductSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta :
        model = Product
        fields = ["id","name","price","category","image","description","user_name","user_image","rate"]
        read_only_fields  = ["user_image","user_name","rate"]
        extra_kwargs = {
            "category": {"write_only": True},
            "description": {"write_only": True},}
        
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None

class ProductAuctionSerializer(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    product_type= serializers.SerializerMethodField()
    class Meta :
        model = ProductAuction
        fields = ["id","name","current_price","inital_price","category","image",
                "description","user_name","user_image","product_type","end_date","activate"]
        read_only_fields  = ["user_image","user_name","current_price","activate"]
        extra_kwargs = {
            "category": {"write_only": True},
            "inital_price": {"write_only": True},
            "description": {"write_only": True},}
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None
    def get_product_type(self, obj):
        return "AuctionProduct"    
    def validate(self, data):
        # تحقق من أن الحقل current_price فارغ
        if not data.get("current_price"):
            data["current_price"] = data.get("inital_price")  # تعيين قيمة initial_price كافتراضية
        return data
    
    
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
    
class ProductAuctionDetailsSerializer(serializers.ModelSerializer):
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    product_type= serializers.SerializerMethodField()
    class Meta :
        model = ProductAuction
        fields = ["name","current_price","inital_price","category","image",
                "description","buyer","user_name","user_image","product_type","end_date","start_date","activate"]
        read_only_fields  = ["current_price","inital_price","image",
                "category","user_name","user_image","product_type","end_date","start_date","buyer","activate"]
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None
    def get_product_type(self, obj):
        return "AuctionProduct"    