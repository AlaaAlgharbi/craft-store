from email.mime import image
from rest_framework import serializers
from .models import CustomUser , Product , ProductAuction , Chat , Comment, ProductRating, Notification
from django.utils.timezone import now
from django.utils import timezone

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
    
class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "creator", "content"]
   
   
class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ["id", "user", "rating"]
        read_only_fields = ["user", "created_at"]   
    
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
    activate = serializers.SerializerMethodField()
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
    def get_activate(self, obj):
        # تحقق مما إذا كان الوقت الحالي أقل من end_date
        return now() < obj.end_date if obj.end_date else False
    def validate(self, data):
        # تحقق من أن الحقل current_price فارغ
        if not data.get("current_price"):
            data["current_price"] = data.get("inital_price")  # تعيين قيمة initial_price كافتراضية
        return data
    
    
class ProductDetailSerializer(serializers.ModelSerializer):
    ratings = ProductRatingSerializer(many=True, read_only=True)
    rate = serializers.SerializerMethodField()
    comment = CommentSerializer(many=True, required=False)
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta : 
        model = Product
        fields = ["name","price","category","image","description","comment","ratings",
                "user_name","user_image","rate","created_at"]
        read_only_fields = ["rate","created_at","user_name","user_image"]
        extra_kwargs = {
            "name": {"required": False},
            "price": {"required": False},
            "category": {"required": False},
        }
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None 
    
    def get_rate(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            return sum(rating.rating for rating in ratings) / ratings.count()
        return 0.0 
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # إزالة حقل ratings من النتيجة النهائية
        representation.pop("ratings", None)
        return representation
    
    def update(self, instance, validated_data):
        for field in ["name", "price", "category"]:
            if field not in validated_data or not validated_data.get(field):
                validated_data[field] = getattr(instance, field)
        comments_data = validated_data.pop("comment", [])
        instance = super().update(instance, validated_data)

        for comment in comments_data:
            if not comment.get("id"):  
                Comment.objects.create(content_object=instance,
                creator=self.context["request"].user,**comment)
        return instance
    
class ProductAuctionDetailsSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    start_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    product_type= serializers.SerializerMethodField()
    countdown = serializers.SerializerMethodField()
    activate = serializers.SerializerMethodField()
    
    class Meta :
        model = ProductAuction
        fields = ["name","current_price","inital_price","category","image","comment",
                "description","buyer","user_name","user_image","product_type","end_date","start_date","activate","countdown"]
        read_only_fields  = ["current_price","inital_price","image",
                "category","user_name","user_image","product_type","end_date","start_date","buyer","activate"]
        extra_kwargs = {
            "name": {"required": False}
            }    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None
    
    def get_product_type(self, obj):
        return "AuctionProduct"    
    
    def get_activate(self, obj):
        return now() < obj.end_date if obj.end_date else False
    
    def get_countdown(self, obj):
        if not obj.end_date:
            return None
        
        now = timezone.now()
        time_left = obj.end_date - now
        
        if time_left.total_seconds() <= 0:
            return "Auction ended"
            
        days = time_left.days
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        seconds = time_left.seconds % 60
        
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            }    
    def update(self, instance, validated_data):
        for field in ["name"]:
            if field not in validated_data or not validated_data.get(field):
                validated_data[field] = getattr(instance, field)
        comments_data = validated_data.pop("comment", [])
        instance = super().update(instance, validated_data)

        for comment in comments_data:
            if not comment.get("id"):  
                Comment.objects.create(content_object=instance,
                creator=self.context["request"].user,**comment)
        return instance
    
class ChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_username = serializers.CharField(write_only=True)
  

    class Meta:
        model = Chat
        fields = ['id', 'sender', 'receiver', 'receiver_username', 'message', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'receiver', 'timestamp']

    def create(self, validated_data):
        receiver_username = validated_data.pop('receiver_username')
        try:
            receiver = CustomUser.objects.get(username=receiver_username)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({'receiver_username': 'User not found'})
        
        validated_data['sender'] = self.context['request'].user
        validated_data['receiver'] = receiver
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['timestamp'] = instance.timestamp.isoformat()
        return representation    
    
class NotificationSerializer(serializers.ModelSerializer):
    auction = ProductAuctionSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'is_read', 'created_at', 'auction']
        read_only_fields = ['id', 'created_at']
    
