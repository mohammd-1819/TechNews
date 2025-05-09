from rest_framework.generics import ListAPIView
from news.serializers.news_ser import NewsSerializer
from news.models.news_model import News
from utility.pagination import Pagination
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from news.filters import NewsFilter


@extend_schema(
    tags=['News'],
    summary='List of all news',
    responses={200: NewsSerializer},
    parameters=[
        OpenApiParameter(name='tags', description='Filter by exact tag name', type=str),
        OpenApiParameter(name='tags_list', description='Filter by multiple tags (comma separated)', type=str),
        OpenApiParameter(name='keyword', description='Filter by single keyword in content', type=str),
        OpenApiParameter(name='keywords',
                         description='Filter by multiple keywords (comma separated) in content or title', type=str),
        OpenApiParameter(name='exclude_keyword', description='Exclude news containing specific keyword', type=str),
        OpenApiParameter(name='exclude_keywords',
                         description='Exclude news containing any of these keywords (comma separated)', type=str),
    ]
)
class NewsListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsSerializer
    queryset = News.objects.all().order_by('-created_at')
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsFilter
    search_fields = ['title', 'tags']
    ordering_fields = ['created_at', 'updated_at']
