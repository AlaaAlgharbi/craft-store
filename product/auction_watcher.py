# import time
# from django.utils import timezone


# def auction_watcher():
#     from .models import ProductAuction, Notification
#     while True:
#         now = timezone.now()
#         auctions = ProductAuction.objects.filter(
#             end_date__lte=now
#         ).exclude(notifications__notification_type="auction_end")
#         for auction in auctions:
#             # إشعارات للفائز والمالك
#             if auction.buyer:
#                 Notification.objects.create(
#                     user=auction.buyer,
#                     auction=auction,
#                     notification_type="auction_won",
#                     message=f"Congratulations! You won the auction for {auction.user} the auction name is {auction.name}",
#                 )

#             Notification.objects.create(
#                 user=auction.user,
#                 auction=auction,
#                 notification_type="auction_end",
#                 message=f"your auction {auction.name} is end , and {auction.buyer} win the auction"
#             )

#         time.sleep(30)  
