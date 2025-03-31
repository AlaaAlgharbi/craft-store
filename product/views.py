from rest_framework import generics
from .serializers import *
from .models import CustomUser
from .permissions import AuthorModifyOrReadOnly1,AuthorModifyOrReadOnly2
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserList(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_field="username"
    permission_classes = [AuthorModifyOrReadOnly2]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class ProductList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProdutDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthorModifyOrReadOnly1]
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer