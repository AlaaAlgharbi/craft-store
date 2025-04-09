from django.shortcuts import get_object_or_404
from rest_framework import generics
from .serializers import *
from .models import CustomUser, Chat
from .permissions import (
    AuthorModifyOrReadOnly1,
    AuthorModifyOrReadOnly2,
    IsCommentCreator,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models


class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "username"
    permission_classes = [AuthorModifyOrReadOnly2]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class AllProductsView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        auction_products = ProductAuction.objects.all()

        product_serializer = ProductSerializer(products, many=True)
        auction_product_serializer = ProductAuctionSerializer(
            auction_products, many=True
        )

        # دمج البيانات
        combined_data = product_serializer.data + auction_product_serializer.data

        # ترتيب المنتجات بناءً على ترتيب الإدخال باستخدام الحقل id
        sorted_data = sorted(combined_data, key=lambda x: x["id"])

        # إرجاع البيانات مرتبة
        return Response(sorted_data)


class ProductRatingCreateView(generics.CreateAPIView):

    serializer_class = ProductRatingSerializer

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        rating_value = request.data.get("rating")

        rating_instance, created = ProductRating.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                "rating": rating_value,
            },
        )

        serializer = ProductRatingSerializer(rating_instance)
        return Response(serializer.data, status=201 if created else 200)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        return Chat.objects.filter(models.Q(sender=user)).order_by("-timestamp")


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


class SearchAllView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        search_query = self.kwargs.get("query", "").lower()

        # Search in users
        users = CustomUser.objects.filter(
            models.Q(username__icontains=search_query)
            | models.Q(first_name__icontains=search_query)
        ).exclude(id=self.request.user.id)

        # Search in products
        products = Product.objects.filter(models.Q(name__icontains=search_query))

        # Combine results with type information
        results = []
        for user in users:
            results.append({"type": "user", "data": UserSerializer(user).data})

        for product in products:
            results.append({"type": "product", "data": ProductSerializer(product).data})

        return results

    def list(self, request, *args, **kwargs):
        results = self.get_queryset()
        if not results:
            return Response({"message": "No results found"}, status=200)
        return Response(results)


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
