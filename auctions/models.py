from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # watchers and seller (both class User) may conflict with each other? or maybe the related names being different avoids that issue? 
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchers", db_table="watched")
    # name = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.id}: {self.username}"


class Listing(models.Model):
    item = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    image_URL = models.URLField(blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    is_open = models.BooleanField(default=True)
    highest_bid = models.ForeignKey('Bid', on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name="highest_bid")
    def __str__(self):
        return f"{self.id}: {self.item} by {self.seller.username}"


class Bid(models.Model):
    bid = models.DecimalField(max_digits=12, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    def __str__(self):
        return f"{self.id}: {self.bid} for {self.listing.item} by {self.bidder.username}"


class Comment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commments")
    datetime_created = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.id}: in {self.listing.item} by {self.commenter.username}"


class Category(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.id}: {self.name}"

