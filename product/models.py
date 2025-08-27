from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete,pre_save
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
    email = models.EmailField(max_length=50, blank=False, null=False, unique=True)
    rate = models.FloatField(default=0.0, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
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

class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transfer_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self):
        if self.status == 'pending':
            self.user.balance += self.amount
            self.user.save()
            self.status = 'approved'
            self.reviewed_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

class Comment(models.Model):
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    rate = models.FloatField(default=0.0, blank=True, null=True)
    def __str__(self):
        return self.content


class Product(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)
    comment = GenericRelation(Comment)
    comment_rate = models.FloatField(default=0.0, blank=True, null=True)
    def __str__(self):
        return self.name


class UserRating(models.Model):
    rater = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ("rater", "user")


class ProductAuction(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    initial_price = models.IntegerField()
    current_price = models.IntegerField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="auctions_created")
    comment = GenericRelation(Comment)
    comment_rate = models.FloatField(default=0.0, blank=True, null=True)
    is_notified = models.BooleanField(default=False)
    buyer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name="auctions_won",
        blank=True,
        null=True,
    )
    def __str__(self):
        return self.name


@receiver([post_save, post_delete], sender=Comment)
def update_comment_rate(sender, instance, **kwargs):
    # الحصول على الكائن المرتبط بالتعليق (Product أو ProductAuction)
    content_object = instance.content_object
    # التأكد من أن الكائن لديه الحقل comment_rate (بمعناه أنه من النماذج التي تريد تحديثها)
    if hasattr(content_object, "comment_rate"):
        # حساب المتوسط لتقييمات التعليقات المرتبطة
        aggregate_result = content_object.comment.aggregate(avg_rate=Avg("rate"))
        avg_rate = aggregate_result["avg_rate"] or 0.0
        # تحديث الحقل comment_rate وحفظ الكائن
        content_object.comment_rate = avg_rate
        content_object.save()

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


@receiver(post_save, sender=UserRating)
def update_user_rate_on_save(sender, instance, created, **kwargs):
    user = instance.user
    avg_rate = (
        UserRating.objects.filter(user=user).aggregate(avg=Avg("rating"))[
            "avg"
        ]
        or 0.0
    )
    user.rate = avg_rate
    user.save()


@receiver(post_delete, sender=UserRating)
def update_user_rate_on_delete(sender, instance, **kwargs):
    user = instance.user
    avg_rate = (
        UserRating.objects.filter(user=user).aggregate(avg=Avg("rating"))[
            "avg"
        ]
        or 0.0
    )
    user.rate = avg_rate
    user.save()


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("auction_end", "Auction Ended"),
        ("outbid", "You Were Outbid"),
        ("auction_won", "You Won the Auction"),
        ("transfer_request", "The request is pending"),
        ("transfer_status", "The transfer status"),
    )

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="notifications"
    )
    auction = models.ForeignKey(
        ProductAuction, on_delete=models.CASCADE, related_name="notifications",null=True,blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"

@receiver(pre_save, sender=ProductAuction)
def cache_previous_buyer(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = ProductAuction.objects.get(pk=instance.pk)
            instance._previous_buyer = previous.buyer
        except ProductAuction.DoesNotExist:
            instance._previous_buyer = None

# Signal for when a bid is placed
@receiver(post_save, sender=ProductAuction)
def notify_previous_bidder(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_previous_buyer'):
        previous_buyer = instance._previous_buyer
        current_buyer = instance.buyer

        if previous_buyer and previous_buyer != current_buyer:
            Notification.objects.create(
                user=previous_buyer,
                auction=instance,
                notification_type="outbid",
                message=f"You were outbid on {instance.name}. Current price: {instance.current_price}", )

