from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from news.models.news_model import News
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema


class RemoveNewsView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        summary='Remove News',
    )
    def delete(self, request, news_id):
        news = get_object_or_404(News, id=news_id)
        news.delete()

        return Response({'message': 'News Removed'}, status=status.HTTP_200_OK)
