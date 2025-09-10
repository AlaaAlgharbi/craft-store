from django.urls import path, include
from .views import *
from rest_framework.authtoken import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="artiauct",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("users/<str:username>/", UserDetail.as_view(), name="user_detail"),
    # path("users/", UserList.as_view(), name="user_list"),
    path("products/", AllProductsView.as_view(), name="Product_List"),
    path("create/products/", ProductCreate.as_view(), name="Product_Create"),
    path("create/auction/", ProductAuctionCreate.as_view(), name="ProductAuction_Create"),
    path("products/<int:pk>/", ProductDetails.as_view(), name="product_detail"),
    path("auction/<int:pk>/bid/",AuctionBidView.as_view(),name="auction-bid"),
    path("user/<str:username>/rate/",UserRatingCreateView.as_view(), name="user-rate"),
    path("auction/<int:pk>/", ProductAuctionDetails.as_view(), name="productAuction_detail"),
    path("delete_comment/<int:pk>/", CommentDelete.as_view(), name="delete_comment"),
    path("search/", SearchAllView.as_view(), name="user-search"),
    path("chat/", ChatListCreateView.as_view(), name="chat-list-create"), #انشاء رسالة
    path("chat/<int:pk>/", ChatDetailView.as_view(), name="chat-detail"),#عرض محتواه الرسالة
    path("chat/user/<str:username>/", UserChatListView.as_view(), name="user-chat-list"),#محادثتي مع فلان
    path("chat/search/<str:user>/", SearchChatView.as_view(), name="message-search"),#البحث عن رسالة
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/delete/<int:pk>/", NotificationDelete.as_view(), name="notification-delete"),
    path("notifications/delete-all/", NotificationDeleteAll.as_view(), name="notification-delete-all"),
    # path("notifications/<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    # path("notifications/unread-count/", UnreadNotificationCount.as_view(), name="unread-count"),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('register/verify-otp/', VerifyRegistrationOTPView.as_view(), name='verify-registration-otp'),
    path('forget/', ForgetPasswordView.as_view(), name='forget_password'),
    path("forget/<str:email>/", ResetPasswordView.as_view(), name="Reset-Password"),
    path("wishlist/", WishlistListCreateView.as_view(), name="wishlist"),
    path("wishlist/<int:product_id>/", WishlistDestroyView.as_view(), name="wishlist-product"),
    path('transfer/create/', TransferRequestCreateView.as_view(), name='transfer_create'),
    path('transfer/', TransferRequestListView.as_view(), name='transfer_pending'),
    path('transfer/<int:pk>/', TransferReviewView.as_view(), name='transfer_review'),
]


urlpatterns += [
    path("auth/", include("rest_framework.urls")),
    path("token-auth/",  CustomAuthToken.as_view(),name="login",),
    path("products/<str:category>/",AllProductsView.as_view(),name="posts-by-category",),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
