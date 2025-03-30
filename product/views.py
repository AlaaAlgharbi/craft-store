from rest_framework import generics
from .serializers import *
from .models import CustomUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated

class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="username"
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProdutDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer