from django.db import models
from product.models import category, Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

# Create your models here.


class ProductAuction(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=True, null=True)
    inital_price = models.IntegerField()
    current_price = models.IntegerField()
    end_date = models.DateTimeField()
    start_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50, choices=category, null=True)
    img = models.ImageField(null=True, blank=True, upload_to='photos')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = GenericRelation(Comment)
