from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Developer(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    foundingdate = models.DateField('date founded', blank=True, null=True)

    def __str__(self):
        return self.title


class Company(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    foundingdate = models.DateField('date founded', blank=True, null=True)

    def __str__(self):
        return self.title


class Game(models.Model):
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    releasedate = models.DateField('date released', blank=True, null=True)

    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, blank=True, null=True)
    publisher = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    type = models.CharField(max_length=10)

    title = models.CharField(max_length=60)
    content = models.TextField(blank=True, null=True)
    pubdate = models.DateTimeField('date published', blank=True, null=True)

    status = models.CharField(max_length=10, blank=True, null=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return self.title

