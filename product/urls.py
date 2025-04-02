from django.urls import path, include
from .views import *

urlpatterns = [
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/", UserList.as_view(), name="user_list"),
    path("products/",AllProductsView.as_view(), name="Product_List"),
    path("create/products/", ProductCreate.as_view(), name="Product_Create"),
    path("create/auction/", ProductAuctionCreate.as_view(), name="ProductAuction_Create"),
    path("products/<int:pk>", ProdutDetails.as_view(), name="product_detail"),
    path("auction/<int:pk>", ProdutAuctionDetails.as_view(), name="productAuction_detail"),
]


urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    ]