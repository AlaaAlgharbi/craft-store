from django.urls import path, include
from .views import *

urlpatterns = [
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/", UserList.as_view(), name="user_list"),
    path("products/", ProductList.as_view(), name="product_List"),
    path("products/<int:pk>", ProdutDetails.as_view(), name="product_detail"),
]
