from email.mime import image
from rest_framework import serializers
from .models import CustomUser , Product , ProductAuction , Chat , Comment, UserRating, Notification
from django.utils.timezone import now
from django.utils import timezone
from .sentiment_analysis_utils import get_sentiment

class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = ["rater", "user", "rating"]
        read_only_fields = ["rater","user"] 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username","first_name","phone_number","image","rate","password","email"]
        read_only_fields = ['rate']
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
class UserDetailSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    auction_products = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'first_name', 
                'phone_number', 'image', 'rate', 'products', 'auction_products']
        read_only_fields = ['products', 'auction_products']
        extra_kwargs = {"password": {"write_only": True}}

    def get_products(self, obj):
        products = Product.objects.filter(user=obj).order_by("-created_at")  # ترتيب من الأحدث للأقدم
        return ProductSerializer(products, many=True).data

    def get_auction_products(self, obj):
        auction_products = ProductAuction.objects.filter(user=obj).order_by("-created_at")  # ترتيب من الأحدث للأقدم
        return ProductAuctionSerializer(auction_products, many=True).data    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # دمج المنتجات والمزادات في قائمة واحدة مرتبة حسب التاريخ
        all_products = representation.get("products", []) + representation.get("auction_products", [])
        all_products.sort(key=lambda x: x["created_at"], reverse=True)  # ترتيب من الأحدث إلى الأقدم
        # إزالة `created_at` من قائمة المنتجات
        for product in all_products:
            product.pop("created_at", None)
        
        # تحديث التمثيل ليحتوي على قائمة واحدة فقط
        representation["all_products"] = all_products
        representation.pop("products", None)
        representation.pop("auction_products", None)
        
        return representation
    
class CommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    creator = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "creator", "content"]
    def get_creator(self,obj):
        return obj.creator.username if obj.creator else None
class ProductSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta :
        model = Product
        fields = ["name","price","created_at","category","image","description","user_name","user_image"]
        read_only_fields  = ["user_image","user_name"]
        extra_kwargs = {
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
        fields = ["name","current_price","created_at","initial_price","category","image",
                "description","user_name","user_image","product_type","end_date","activate"]
        read_only_fields  = ["user_image","user_name","current_price","activate"]
        extra_kwargs = {
            "initial_price": {"write_only": True},
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
            data["current_price"] = data.get("initial_price")  # تعيين قيمة initial_price كافتراضية
        return data
    
    
class ProductDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    comment = CommentSerializer(many=True, required=False)
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    class Meta : 
        model = Product
        fields = ["name","price","category","image","description","comment","comment_rate",
                "user_name","user_image","created_at"]
        read_only_fields = ["created_at","user_name","user_image","comment_rate"]
        extra_kwargs = {
            "name": {"required": False},
            "price": {"required": False},
            "category": {"required": False},
        }
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    def get_user_image(self, obj):
        return obj.user.image.url if obj.user and obj.user.image else None 
    
    def update(self, instance, validated_data):
        for field in ["name", "price", "category"]:
            if field not in validated_data or not validated_data.get(field):
                validated_data[field] = getattr(instance, field)
        comments_data = validated_data.pop("comment", [])
        instance = super().update(instance, validated_data)

        for comment in comments_data:
            if not comment.get("id"): 
                comment_rate=get_sentiment(comment.get("content"))
                Comment.objects.create(content_object=instance,
                creator=self.context["request"].user,rate=comment_rate,**comment)
        return instance
    
    
class ProductAuctionDetailsSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M",read_only=True)
    user_name = serializers.SerializerMethodField()
    buyer = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    product_type= serializers.SerializerMethodField()
    countdown = serializers.SerializerMethodField()
    activate = serializers.SerializerMethodField()
    class Meta :
        model = ProductAuction
        fields = ["name","current_price","initial_price","category","image","comment","comment_rate",
                "description","buyer","user_name","user_image","product_type","end_date","created_at","activate","countdown"]
        read_only_fields  = ["current_price","initial_price","image",
                "category","user_name","user_image","product_type","end_date","created_at","buyer","activate","comment_rate"]
        extra_kwargs = {
            "name": {"required": False}
            }    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else None
    
    def get_buyer(self, obj):
        return obj.buyer.username if obj.buyer else None
    
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
                comment_rate=get_sentiment(comment.get("content"))
                Comment.objects.create(content_object=instance,
                creator=self.context["request"].user,rate=comment_rate,**comment)
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
    
    
class OTPSendSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    otp_code = serializers.CharField(max_length=10)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)

