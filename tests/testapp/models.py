# Django
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
