from django.urls import path, include
from .views import UserDetail,UserCreate,UserList

urlpatterns = [
    path("users/create",UserCreate.as_view(), name="user_create"),
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/",UserList.as_view(), name="user_list"),
]