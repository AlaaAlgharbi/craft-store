import time
from django.utils import timezone
from django.db import transaction


def auction_watcher():
    from .models import ProductAuction, Notification
    while True:
        now = timezone.now()
        auctions = ProductAuction.objects.filter(
        end_date__lte=now,is_notified=False)
        for auction in auctions:
            with transaction.atomic():
                if auction.buyer:
                    buyer = auction.buyer
                    owner = auction.user
                    amount = auction.current_price

                    if buyer.balance >= amount:
                        buyer.balance -= amount
                        owner.balance += amount
                        buyer.save()
                        owner.save()

                        Notification.objects.create(
                            user=buyer,
                            auction=auction,
                            notification_type="auction_won",
                            message=f"Congratulations! You won the auction for {owner.username}. The auction name is {auction.name}",
                        )

                        Notification.objects.create(
                            user=owner,
                            auction=auction,
                            notification_type="auction_end",
                            message=f"Your auction {auction.name} has ended, and {buyer.username} won the auction.",
                        )
                else:
                    Notification.objects.create(
                        user=auction.user,
                        auction=auction,
                        notification_type="auction_end",
                        message=f"Your auction {auction.name} has ended, but no one placed a winning bid.",
                    )

                auction.is_notified = True
                auction.save()
        time.sleep(30)
