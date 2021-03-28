from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Item(models.Model):
    name = models.CharField(max_length=12)
    description = models.CharField(max_length=255, default=None)
    category = models.CharField(max_length=12, default=None)
    startingbid = models.DecimalField(max_digits=6, decimal_places=2, default=None)
    image = models.URLField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    author = models.IntegerField(default=None, blank=True, null=True)

class Bid(models.Model):
    item_id = models.IntegerField(blank = True, default=None)
    bid = models.DecimalField(max_digits=5, decimal_places=2)
    user_id = models.IntegerField(blank = True, default=None)
    winner = models.BooleanField(default=False)

class Comment(models.Model):
    content = models.CharField(max_length=255)
    user_id = models.ForeignKey(User, on_delete = models.CASCADE)
    item_id = models.IntegerField(blank = True, default= None)
    datetime = models.DateTimeField(blank = True, auto_now_add=True)

class Watchlist(models.Model):
    user_id = models.IntegerField(blank = True)
    item_id = models.IntegerField(blank = True)