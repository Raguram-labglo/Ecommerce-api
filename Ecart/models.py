from email.policy import default
from operator import mod
from django.db import models
from django.contrib.auth.models import User

failed = 0
pending = 1
success = 2

order = [(pending, 'pending'), 
        (success, 'success'),
        (failed, 'failed')]


class Product(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="prodects_img/", null=True)
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=40)
    price = models.IntegerField()
    in_stocks = models.BooleanField(default = True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,  null=True, on_delete=models.CASCADE)
    price = models.FloatField(null=True)
    quantity = models.IntegerField(default=1)
    status = models.IntegerField(choices=order, default=pending)
    is_active = models.BooleanField(default=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_items = models.ManyToManyField(Cart)
    order_status = models.IntegerField(choices=order, default=pending)
    order_price = models.IntegerField(null=True)
    tax_price = models.IntegerField(null=True)
    order_time = models.DateTimeField(auto_now_add=True)


class Wish(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    favourite = models.ManyToManyField(Product)
    wished = models.BooleanField(default=True)
