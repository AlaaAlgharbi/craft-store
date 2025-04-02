from rest_framework import generics
from .serializers import *
from .models import CustomUser
from .permissions import AuthorModifyOrReadOnly1,AuthorModifyOrReadOnly2
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="username"
    permission_classes = [AuthorModifyOrReadOnly2]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class AllProductsView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        auction_products = ProductAuction.objects.all()

        product_serializer = ProductSerializer(products, many=True)
        auction_product_serializer = ProductAuctionSerializer(auction_products, many=True)

        # دمج البيانات
        combined_data = product_serializer.data + auction_product_serializer.data
        
        # ترتيب المنتجات بناءً على ترتيب الإدخال باستخدام الحقل id
        sorted_data = sorted(combined_data, key=lambda x: x['id'])

        # إرجاع البيانات مرتبة
        return Response(sorted_data)


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

class ProdutDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthorModifyOrReadOnly1]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    
class ProdutAuctionDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthorModifyOrReadOnly1]
    queryset = ProductAuction.objects.all()
    serializer_class = ProductAuctionDetailsSerializer    