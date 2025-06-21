from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import *
from .models import CustomUser, Chat, Notification
from .permissions import (
    AuthorModifyOrReadOnly1,
    AuthorModifyOrReadOnly2,
    IsCommentCreator,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from rest_framework import status
from .utils import send_otp, verify_otp
from .image_search_utils import search_similar_products
from django.db.models import Q

class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "username"
    permission_classes = [AuthorModifyOrReadOnly2]
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        new_email = request.data.get("email")  # استخراج البريد الجديد من الطلب

        if new_email and new_email != instance.email:
            # إذا تغيّر البريد، قم بإرسال رمز تحقق وجعل الحساب غير نشط
            instance.is_active = False
            instance.email = new_email
            instance.save()
            otp_status = send_otp(instance)
            if otp_status:
                return Response(
                    {
                        "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني الجديد. الحساب غير نشط حتى يتم التحقق."
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "message": "فشل إرسال رمز التحقق. البريد الإلكتروني لم يتم تغييره."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # إذا لم يتم تغيير البريد الإلكتروني، قم بتحديث البيانات الأخرى فقط
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AllProductsView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        auction_products = ProductAuction.objects.all()

        # Serialize data
        product_serializer = ProductSerializer(products, many=True)
        auction_product_serializer = ProductAuctionSerializer(
            auction_products, many=True
        )

        combined_data = product_serializer.data + auction_product_serializer.data

        # الحصول على الفئة إذا تم تمريرها
        category = self.kwargs.get("category")

        if category:
            combined_data = [
                item for item in combined_data if item.get("category") == category
            ]

        # الحصول على قيم الأسعار من المعلمات
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if min_price and max_price:
            min_price = float(min_price)
            max_price = float(max_price)
            # تصفية المنتجات حسب نطاق السعر
            combined_data = [
                item
                for item in combined_data
                if min_price <= item.get("price", 0) <= max_price
                or min_price <= item.get("current_price", 0) <= max_price
            ]

        only_products = request.query_params.get("only_products")
        if only_products == "true":
            combined_data = [item for item in combined_data if item.get("product_type")]
        # ترتيب المنتجات حسب تاريخ الإنشاء
        sorted_data = sorted(
            combined_data, key=lambda x: x.get("created_at", ""), reverse=True
        )

        # إزالة المفاتيح غير المطلوبة
        cleaned_data = [
            {
                key: value
                for key, value in item.items()
                if key not in ["category", "created_at"]
            }
            for item in sorted_data
        ]

        return Response(cleaned_data)

class UserRatingCreateView(generics.CreateAPIView):
    serializer_class = UserRatingSerializer

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, username=kwargs.get("username"))
        rating_value = request.data.get("rating")

        rating_instance, created = UserRating.objects.update_or_create(
            user=user,
            rater=request.user,
            defaults={"rating": rating_value},
        )

        serializer = UserRatingSerializer(rating_instance)
        return Response(serializer.data, status=201 if created else 200)

    def perform_create(self, serializer):
        serializer.save(rater=self.request.user)


class ProductCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductAuctionCreate(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ProductAuction.objects.all()
    serializer_class = ProductAuctionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthorModifyOrReadOnly1]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class CommentDelete(generics.DestroyAPIView):
    permission_classes = [IsCommentCreator]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class ProductAuctionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthorModifyOrReadOnly1]
    queryset = ProductAuction.objects.all()
    serializer_class = ProductAuctionDetailsSerializer


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # return Chat.objects.filter(models.Q(sender=user)).order_by("-timestamp")
        return Chat.objects.filter(models.Q(sender=user) | models.Q(receiver=user)).order_by("-timestamp")


class ChatDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(models.Q(sender=user) | models.Q(receiver=user))


class UserChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs["user_id"]
        return Chat.objects.filter(
            (models.Q(sender=user) & models.Q(receiver_id=other_user_id))
            | (models.Q(sender_id=other_user_id) & models.Q(receiver=user))
        ).order_by("-timestamp")


class SearchAllView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        يسمح البحث النصي عبر query parameter
        Example: GET /api/hybrid-search/?query=سماعة
        """
        text_query = request.query_params.get('query', '').strip().lower()
        text_results = []
        if text_query:
            # البحث النصي في المنتجات
            products = Product.objects.filter(Q(name__icontains=text_query))
            auction_products = ProductAuction.objects.filter(Q(name__icontains=text_query))
            users = CustomUser.objects.filter(Q(username__icontains=text_query)
                                        | models.Q(first_name__icontains=text_query))
            # استخدام serializers لإرجاع البيانات
            prod_ser = ProductSerializer(products, many=True).data
            auc_ser = ProductAuctionSerializer(auction_products, many=True).data
            user_ser=UserSerializer(users,many=True).data
            # يمكنك إضافة مفتاح لتحديد نوع النتيجة (product أو auction)
            for item in prod_ser:
                item['type'] = 'product'
                text_results.append(item)
            for item in auc_ser:
                item['type'] = 'auction'
                text_results.append(item)
            for item in user_ser:
                item['type'] = 'user'
                text_results.append(item)
        
        return Response({
            "text_search_results": text_results
        })

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image', None)
        if not image_file:
            return Response({"error": "يجب إرسال صورة للبحث."}, status=400)

        try:
            image_results = search_similar_products(image_file, distance_threshold=55)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        serialized_results = []
        for obj in image_results:
            if isinstance(obj, Product):
                data = ProductSerializer(obj).data
                data["type"] = "product"
            elif isinstance(obj, ProductAuction):
                data = ProductAuctionSerializer(obj).data
                data["type"] = "auction"    
            else:
                continue
            serialized_results.append(data)

        return Response({
            "image_search_results": serialized_results
        })

class SearchMessageView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        search_query = self.kwargs.get("message", "").lower()
        user = self.request.user

        return Chat.objects.filter(
            models.Q(message__icontains=search_query)
            & (models.Q(sender=user) | models.Q(receiver=user))
        ).order_by("-timestamp")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No messages found"}, status=200)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(is_read=True)


class UnreadNotificationCount(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count})


class UserRegistrationView(generics.CreateAPIView):
    # queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # إنشاء المستخدم مع ضبط is_active=False
            user = serializer.save()
            user.is_active = False
            user.save()
            # إرسال OTP إلى ايميل  المدخل
            otp_status = send_otp(user)
            if otp_status:
                return Response(
                    {
                        "message": "تم إرسال OTP بنجاح، يرجى التحقق من هاتفك.",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                # في حال فشل إرسال OTP، يُمكن إلغاء إنشاء الحساب
                user.delete()
                return Response(
                    {"message": "فشل إرسال OTP. يرجى المحاولة مرة أخرى."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyRegistrationOTPView(generics.CreateAPIView):
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data["otp_code"]
            email = serializer.validated_data["email"]
            if verify_otp(email, otp_code):
                try:
                    user = CustomUser.objects.get(email=email, is_active=False)
                    user.is_active = True
                    user.save()
                    # حذف البريد الإلكتروني من الجلسة بعد التحقق
                    return Response(
                        {"message": "تم التحقق من OTP وتفعيل الحساب بنجاح!"},
                        status=status.HTTP_200_OK,
                    )
                except CustomUser.DoesNotExist:
                    return Response(
                        {"message": "لا يوجد حساب مرتبط بهذا البريد يحتاج للتفعيل."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {"message": "الرمز المدخل غير صحيح. يرجى المحاولة مرة أخرى."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(generics.CreateAPIView):
    serializer_class = OTPSendSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_object_or_404(CustomUser, email=email)

        # محاولة إرسال رمز التحقق OTP للمستخدم
        otp_status = send_otp(user)
        if otp_status:
            return Response(
                {"message": "تم إرسال OTP بنجاح، يرجى التحقق من هاتفك."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "فشل إرسال OTP. يرجى المحاولة مرة أخرى."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            

class ResetPasswordView(generics.CreateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]  
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user =get_object_or_404(CustomUser,email=email)
        user.set_password(password)
        user.save()

        return Response({"message": "تم تغيير كلمة السر بنجاح"},
                        status=status.HTTP_200_OK)


        
class WishlistListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.wishlist.all()

    def post(self, request):
        product_id = request.data.get("product_id")
        try:
            product=Product.objects.get(id=product_id)
            if product in request.user.wishlist.all():
                return Response(
                    {"message": "Product already in wishlist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.wishlist.add(product_id)
            return Response(
                {"message": "Product added to wishlist."}, status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )



class WishlistDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    def destroy(self, request, *args,**kwaargs):
        product_id=request.data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
            if product not in request.user.wishlist.all():
                return Response(
                    {"message": "Product not in wishlist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.user.wishlist.remove(product)
            return Response(
                {"message": "Product removed from wishlist."}, status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
