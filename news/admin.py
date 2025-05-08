from django.contrib import admin
from news.models.tag_model import Tag
from news.models.news_model import News

admin.site.register(Tag)
admin.site.register(News)
