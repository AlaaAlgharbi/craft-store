from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AbstractUser

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
    rate = models.DecimalField(
        max_digits=2, decimal_places=1, default=0, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE ,null=False)
    comment = GenericRelation(Comment)

    def __str__(self):
        return self.name


class ProductAuction(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    inital_price = models.IntegerField()
    current_price = models.IntegerField()
    end_date = models.DateTimeField()
    start_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to="photos")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user")
    comment = GenericRelation(Comment)
    buyer =models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="buyer",blank=True, null=True)


    def __str__(self):
        return self.name



class Chat(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"

    class Meta:
        ordering = ['-timestamp']