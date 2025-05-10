from drf_spectacular.types import OpenApiTypes
from rest_framework.generics import ListAPIView
from news.serializers.news_ser import NewsSerializer
from news.models.news_model import News
from utility.pagination import Pagination
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from news.filters import NewsFilter
from rest_framework.response import Response


class NewsListView(ListAPIView):
    """
    API view to list and filter news articles.

    This view provides paginated access to all news articles with various filtering options.
    No authentication is required to access this endpoint.
    """
    permission_classes = [AllowAny]
    serializer_class = NewsSerializer
    queryset = News.objects.all().order_by('-created_at')
    pagination_class = Pagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsFilter
    search_fields = ['title', 'tags']
    ordering_fields = ['created_at', 'updated_at']

    @extend_schema(
        tags=['News'],
        operation_id='list_news',
        summary='List all news articles from database',
        description='''
        This endpoint retrieves a paginated list of all news articles with filtering capabilities.

        **Features**:
        - Pagination support
        - Multiple filtering options
        - Tag-based filtering
        - Keyword search in content and title
        - Sorting by creation and update time

        **Filtering Options**:
        - Filter by single or multiple tags
        - Search by keywords in content and title
        - Exclude articles containing specific keywords
        ''',
        parameters=[
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by exact tag name',
                required=False
            ),
            OpenApiParameter(
                name='tags_list',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by multiple tags (comma separated)',
                required=False
            ),
            OpenApiParameter(
                name='keyword',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by single keyword in content',
                required=False
            ),
            OpenApiParameter(
                name='keywords',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by multiple keywords (comma separated) in content or title',
                required=False
            ),
            OpenApiParameter(
                name='exclude_keyword',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Exclude news containing specific keyword',
                required=False
            ),
            OpenApiParameter(
                name='exclude_keywords',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Exclude news containing any of these keywords (comma separated)',
                required=False
            )
        ],
        responses={
            200: OpenApiResponse(
                response=NewsSerializer,
                description='List of news articles retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value=[

                            {
                                "id": "e8bc413e-2b26-49e9-a3da-e0a4dc9f3568",
                                "title": "test news 2",
                                "text": "ergergerg",
                                "source": "test source",
                                "created_at": "2025-05-08T17:44:10.279522Z",
                                "updated_at": "2025-05-08T17:44:10.279522Z",
                                "tags": [
                                    "e34f422a-19a3-4ae6-a998-1254612f5e4a"
                                ]
                            },
                            {
                                "id": "94c9000c-5ef3-443a-9d59-4746e5586d23",
                                "title": "test news 1",
                                "text": "swewgwg  yo",
                                "source": "test source",
                                "created_at": "2025-05-08T17:43:59.377890Z",
                                "updated_at": "2025-05-08T18:03:23.160069Z",
                                "tags": [
                                    "336191bd-e195-41dd-bdbe-c42b4b7a08f6"
                                ]
                            }

                        ],
                        response_only=True
                    )
                ]
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """
        List all news articles with filtering options.

        Args:
            request: HTTP request object

        Returns:
            Response: Paginated list of news articles
        """
        return super().get(request, *args, **kwargs)
