from django.db import models
from .tag_model import Tag


class News(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    source = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, related_name='news')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
