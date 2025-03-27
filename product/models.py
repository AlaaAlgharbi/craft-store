from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.
category = [
    ("Accessories", "Accessories"),
    ("Candle", "Candle"),
    ("Painting", "Painting"),
    ("Wool", "Wool"),
    ("Sweet", "Sweet"),
    ("Carving", "Carving"),
    ("Decoration", "Decoration"),
    ("Bags", "Bags"),
    ("other", "other")
]


class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
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
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category)
    image = models.ImageField(null=True, blank=True, upload_to='photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    comment = GenericRelation(Comment)
    
    def __str__(self):
        return self.id

class ProductAuction(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    inital_price = models.IntegerField()
    current_price = models.IntegerField()
    end_date = models.DateTimeField()
    start_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='user')
    comment = GenericRelation(Comment)
    buyer=models.OneToOneField(User, on_delete=models.CASCADE,related_name='buyer')
    activate=models.BooleanField()
    
    def __str__(self):
        return self.id



