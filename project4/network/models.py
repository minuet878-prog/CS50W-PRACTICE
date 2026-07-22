from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follow = models.ManyToManyField("User", blank=True, related_name="followers")

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    post_time = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField("User", blank=True, related_name="like_posts")


    def __str__(self):
        return f"{self.poster}:{self.content[:30]}"