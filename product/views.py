from rest_framework import generics
from .serializers import *
from .models import CustomUser
from rest_framework.authentication import BaseAuthentication

class UserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SianUpUserSerializer

class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ListUserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="username"
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailsSerializer


class ProductCreat(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class ProdutDetails(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="name"
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
