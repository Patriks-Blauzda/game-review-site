from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Image(models.Model):
    alt_text = models.CharField(max_length=60, blank=True, null=True)
    width = models.PositiveSmallIntegerField(default=128)
    height = models.PositiveSmallIntegerField(default=128)
    binary_blob = models.TextField(editable=True)


class Developer(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    foundingdate = models.DateField('date founded', blank=True, null=True)

    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title

    def __ge__(self, other):
        return self.title.lower() > other.title.lower()


class Publisher(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    foundingdate = models.DateField('date founded', blank=True, null=True)

    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, blank=True, null=True)


class Game(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    releasedate = models.DateField('date released', blank=True, null=True)

    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, blank=True, null=True)

    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return self.title

    def __ge__(self, other):
        return self.title.lower() > other.title.lower()


class Post(models.Model):
    type = models.CharField(max_length=10)

    title = models.CharField(max_length=60)
    content = models.TextField(blank=True, null=True)
    pubdate = models.DateTimeField('date published', blank=True, null=True)

    status = models.CharField(max_length=10, blank=True, null=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
        return self.title


class LikesUserMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)


class DislikesUserMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
