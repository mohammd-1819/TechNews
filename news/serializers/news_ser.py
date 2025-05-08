from rest_framework import serializers
from news.models.news_model import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        exclude = ('id',)
        read_only_fields = ('created_at', 'updated_at')


