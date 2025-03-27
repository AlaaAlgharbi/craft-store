from django.contrib import admin
from .models import Product, Comment,ProductAuction,CustomUser
# Register your models here

admin.site.register(Product)
admin.site.register(Comment)
admin.site.register(ProductAuction)
admin.site.register(CustomUser)

