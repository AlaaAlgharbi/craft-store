from django.urls import path, include
from .views import *

urlpatterns = [
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/", UserList.as_view(), name="user_list"),
    path("products/", AllProductsView.as_view(), name="Product_List"),
    path("create/products/", ProductCreate.as_view(), name="Product_Create"),
    path("create/auction/", ProductAuctionCreate.as_view(), name="ProductAuction_Create"),
    path("products/<int:pk>", ProdutDetails.as_view(), name="product_detail"),
    path("auction/<int:pk>", ProdutAuctionDetails.as_view(), name="productAuction_detail"),
    path("chat/", ChatListCreateView.as_view(), name="chat-list-create"),
    path("chat/<int:pk>/", ChatDetailView.as_view(), name="chat-detail"),
    path("chat/user/<int:user_id>/", UserChatListView.as_view(), name="user-chat-list"),
    path("users/search/<str:username>/", SearchUser.as_view(), name="user-search"),
    path("chat/search/<str:message>/", SearchMessageView.as_view(), name="message-search"),
]


urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    ]
