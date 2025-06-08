from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from django.utils import timezone

category = [
    ("Accessories", "Accessories"),
    ("Candle", "Candle"),
    ("Painting", "Painting"),
    ("Wool", "Wool"),
    ("Sweet", "Sweet"),
    ("Carving", "Carving"),
    ("Decoration", "Decoration"),
    ("Bags", "Bags"),
    ("other", "other"),
]


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=False, null=False)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)
    first_name = models.CharField(max_length=50, blank=False, null=False)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    email = models.CharField(max_length=50, blank=False, null=False, unique=True)
    wishlist = models.ManyToManyField(
        "Product", related_name="wishlisted_by", blank=True
    )
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",
        blank=True,
    )


class Comment(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return self.content


class Product(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.IntegerField()
    rate = models.FloatField(default=0.0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    comment = GenericRelation(Comment)

    def __str__(self):
        return self.name


class ProductRating(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ("product", "user")


class ProductAuction(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    inital_price = models.IntegerField()
    current_price = models.IntegerField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user")
    comment = GenericRelation(Comment)
    buyer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="buyer",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Chat(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"

    class Meta:
        ordering = ["-timestamp"]


class Verify(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="verify"
    )
    token = models.CharField(max_length=6, default="", blank=True)


@receiver(post_save, sender=ProductRating)
def update_product_rate_on_save(sender, instance, created, **kwargs):
    product = instance.product
    avg_rate = (
        ProductRating.objects.filter(product=product).aggregate(avg=Avg("rating"))[
            "avg"
        ]
        or 0.0
    )
    product.rate = avg_rate
    product.save()


@receiver(post_delete, sender=ProductRating)
def update_product_rate_on_delete(sender, instance, **kwargs):
    product = instance.product
    avg_rate = (
        ProductRating.objects.filter(product=product).aggregate(avg=Avg("rating"))[
            "avg"
        ]
        or 0.0
    )
    product.rate = avg_rate
    product.save()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("auction_end", "Auction Ended"),
        ("outbid", "You Were Outbid"),
        ("auction_won", "You Won the Auction"),
        ("auction_lost", "You Lost the Auction"),
    )

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="notifications"
    )
    auction = models.ForeignKey(
        ProductAuction, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"


# Signal for when a bid is placed
@receiver(post_save, sender=ProductAuction)
def handle_auction_bid(sender, instance, created, **kwargs):
    if not created:  # Only for updates
        # Get the previous highest bidder
        previous_bidder = instance.buyer

        # If there was a previous bidder and it's not the current bidder
        if previous_bidder and previous_bidder != instance.buyer:
            # Create outbid notification for the previous bidder
            Notification.objects.create(
                user=previous_bidder,
                auction=instance,
                notification_type="outbid",
                message=f"You were outbid on {instance.name}. Current price: {instance.current_price}",
            )


# Signal for when auction ends
@receiver(post_save, sender=ProductAuction)
def handle_auction_end(sender, instance, created, **kwargs):
    if not created:  # Only for updates
        current_time = timezone.now()

        # Check if auction just ended
        if (
            instance.end_date <= current_time
            and not instance.notifications.filter(
                notification_type="auction_end"
            ).exists()
        ):
            # Create notification for the winner
            if instance.buyer:
                Notification.objects.create(
                    user=instance.buyer,
                    auction=instance,
                    notification_type="auction_won",
                    message=f"Congratulations! You won the auction for {instance.name}",
                )

            # Create notifications for all other bidders
            for bidder in instance.bidders.all():
                if bidder != instance.buyer:
                    Notification.objects.create(
                        user=bidder,
                        auction=instance,
                        notification_type="auction_lost",
                        message=f"You lost the auction for {instance.name}",
                    )
