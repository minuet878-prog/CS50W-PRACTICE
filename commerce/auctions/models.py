from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", blank=True, related_name="watchers")

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Listing(models.Model):
    item = models.CharField(max_length=64)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    create_time = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True)
    description = models.TextField(blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="listings")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.item
    
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid_items")

    def __str__(self):
        return f"{self.bid_price}"

class Comment(models.Model):
    comment = models.TextField()
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_items")
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment