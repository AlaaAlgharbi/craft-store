from rest_framework import generics
from .serializers import UserDetailsSerializer,SianUpUserSerializer,ListUserSerializer
from .models import CustomUser

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