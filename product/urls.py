from django.urls import path, include
from .views import *

urlpatterns = [
    path("users/<str:username>", UserDetail.as_view(), name="user_detail"),
    path("users/", UserList.as_view(), name="user_list"),
    # path("users/<str:username>", UserList.as_view(), name="user_list"),
    path("products/", AllProductsView.as_view(), name="Product_List"),
    path("create/products/", ProductCreate.as_view(), name="Product_Create"),
    path("create/auction/", ProductAuctionCreate.as_view(), name="ProductAuction_Create"),
    path("products/<int:pk>", ProductDetails.as_view(), name="product_detail"),
    path("products/<int:product_id>/rate/", ProductRatingCreateView.as_view(), name="product-rate"),
    path("auction/<int:pk>", ProductAuctionDetails.as_view(), name="productAuction_detail"),
    path("delete_comment/<int:pk>", CommentDelete.as_view(), name="delete_comment"),
    path("chat/", ChatListCreateView.as_view(), name="chat-list-create"),
    path("chat/<int:pk>/", ChatDetailView.as_view(), name="chat-detail"),
    path("chat/user/<int:user_id>/", UserChatListView.as_view(), name="user-chat-list"),
    path("search/<str:query>/", SearchAllView.as_view(), name="user-search"),
    path("chat/search/<str:message>/", ChatListCreateView.as_view(), name="message-search"),
]


urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    ]
