from django.urls import path, include
from .views import *

urlpatterns = [
    path("users/create", UserCreate.as_view(), name="user_create"),
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/", UserList.as_view(), name="user_list"),
    path("product/creat", ProductCreat.as_view(), name="product_creat"),
    path("products/", ProductList.as_view(), name="product_List"),
    path("products/<str:name>", ProdutDetails.as_view(), name="product_detail"),
]
