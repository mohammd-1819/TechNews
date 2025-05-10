from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.views import APIView
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from rest_framework.response import Response
from utility.scraper import scrape_digiato_news


class ScrapedNewsView(APIView):
    """
    API view to scrape and filter news from Digiato with pagination.

    This view provides access to scraped news articles with advanced filtering options.
    No authentication is required to access this endpoint.
    """
    permission_classes = [AllowAny]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        operation_id='scrape_and_filter_news',
        summary='Scrape and filter news from Digiato',
        description='''
        This endpoint scrapes news from Digiato website and returns filtered results without saving to database.

        **Features**:
        - Returns raw scraped data with full article text
        - Advanced filtering support (keywords, exclusions)
        - Pagination support
        - Topic selection support
        - Sorting capabilities
        - No database persistence
        ''',
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number to scrape',
                required=False
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of items per page',
                required=False
            ),
            OpenApiParameter(
                name='topic',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Topic to scrape (default: "tech")',
                required=False
            ),
            OpenApiParameter(
                name='keyword',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by single keyword in content or title',
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
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order results by field (created_at, -created_at, title, -title)',
                required=False
            )
        ],
        responses={
            200: OpenApiResponse(
                description='News scraped and filtered successfully',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value={
                            'count': 20,
                            'next': 'https://api.example.com/scraped-news/?page=2',
                            'previous': None,
                            'results': [
                                {
                                    "id": "94c9000c-5ef3-443a-9d59-4746e5586d23",
                                    "title": "عنوان خبر تست دیگر",
                                    "text": "متن کامل مقاله دوم که شامل چندین پاراگراف است...",
                                    "source": "https://digiato.com/another-example",
                                    "created_at": "2023-05-08T17:43:59.377890Z",
                                    "updated_at": "2023-05-08T17:43:59.377890Z",
                                },
                                {
                                    "id": "94c9000c-5ef3-443a-9d59-4746e5586d23",
                                    "title": "عنوان خبر تست دیگر",
                                    "text": "متن کامل مقاله دوم که شامل چندین پاراگراف است...",
                                    "source": "https://digiato.com/another-example",
                                    "created_at": "2023-05-08T17:43:59.377890Z",
                                    "updated_at": "2023-05-08T17:43:59.377890Z",

                                }
                            ]
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Error in scraping or filtering process',
                examples=[
                    OpenApiExample(
                        'Error Response',
                        value={
                            'error': 'Invalid filter parameters or scraping error'
                        },
                        response_only=True
                    )
                ]
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Scrape news from Digiato, apply filters and return paginated results.

        Args:
            request: HTTP request object with optional query parameters for filtering and pagination

        Returns:
            Response: JSON response with filtered, paginated scraped news data
        """
        try:
            # Get basic parameters
            page_number = request.query_params.get('page', '1')
            try:
                page_number = int(page_number)
                if page_number < 1:
                    return Response(
                        {'error': 'Page number must be a positive integer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid page number'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            topic = request.query_params.get('topic', 'tech')

            # Get page size
            page_size = request.query_params.get('page_size', '10')
            try:
                page_size = int(page_size)
                if page_size < 1 or page_size > 100:
                    return Response(
                        {'error': 'Page size must be between 1 and 100'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Invalid page size'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Scrape news
            news_items = scrape_digiato_news(page_number=page_number, topic=topic)

            # Apply filters
            filtered_items = self.apply_filters(news_items, request.query_params)

            # Apply sorting
            sorted_items = self.apply_sorting(filtered_items, request.query_params.get('ordering'))

            # Apply pagination
            paginated_items = self.paginate_items(sorted_items, page_size, page_number, request)

            return Response(paginated_items, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def apply_filters(self, news_items, query_params):
        """
        Apply keyword filters to the scraped news items.

        Args:
            news_items: List of news items
            query_params: Request query parameters

        Returns:
            Filtered list of news items
        """
        filtered_items = news_items

        # Filter by single keyword
        keyword = query_params.get('keyword')
        if keyword:
            filtered_items = [
                item for item in filtered_items
                if keyword.lower() in item.get('title', '').lower() or
                   keyword.lower() in item.get('content', '').lower() or
                   keyword.lower() in item.get('text', '').lower()
            ]

        # Filter by multiple keywords (any match)
        keywords = query_params.get('keywords')
        if keywords:
            keyword_list = [k.strip().lower() for k in keywords.split(',')]
            filtered_items = [
                item for item in filtered_items
                if any(
                    k in item.get('title', '').lower() or
                    k in item.get('content', '').lower() or
                    k in item.get('text', '').lower()
                    for k in keyword_list
                )
            ]

        # Exclude by single keyword
        exclude_keyword = query_params.get('exclude_keyword')
        if exclude_keyword:
            filtered_items = [
                item for item in filtered_items
                if exclude_keyword.lower() not in item.get('title', '').lower() and
                   exclude_keyword.lower() not in item.get('content', '').lower() and
                   exclude_keyword.lower() not in item.get('text', '').lower()
            ]

        # Exclude by multiple keywords
        exclude_keywords = query_params.get('exclude_keywords')
        if exclude_keywords:
            exclude_keyword_list = [k.strip().lower() for k in exclude_keywords.split(',')]
            filtered_items = [
                item for item in filtered_items
                if not any(
                    k in item.get('title', '').lower() or
                    k in item.get('content', '').lower() or
                    k in item.get('text', '').lower()
                    for k in exclude_keyword_list
                )
            ]

        return filtered_items

    def apply_sorting(self, news_items, ordering):
        """
        Sort the news items based on the ordering parameter.

        Args:
            news_items: List of news items
            ordering: Ordering parameter

        Returns:
            Sorted list of news items
        """
        if not ordering:
            # Default to sorting by created_at (newest first)
            return sorted(news_items, key=lambda x: x.get('created_at', ''), reverse=True)

        reverse = False
        if ordering.startswith('-'):
            reverse = True
            ordering = ordering[1:]

        valid_fields = ['created_at', 'updated_at', 'title', 'published_at']

        if ordering not in valid_fields:
            # Fall back to default if invalid field
            return sorted(news_items, key=lambda x: x.get('created_at', ''), reverse=True)

        return sorted(news_items, key=lambda x: x.get(ordering, ''), reverse=reverse)

    def paginate_items(self, items, page_size, page_number, request):
        """
        Paginate the news items.

        Args:
            items: List of news items
            page_size: Number of items per page
            page_number: Current page number
            request: HTTP request object

        Returns:
            Dictionary with pagination details and results
        """
        total_items = len(items)
        total_pages = (total_items + page_size - 1) // page_size

        start_idx = (page_number - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)

        # Get current page items
        current_page_items = items[start_idx:end_idx]

        # Build next and previous URLs
        base_url = request.build_absolute_uri().split('?')[0]
        query_params = request.query_params.copy()

        # Next page
        next_page = None
        if page_number < total_pages:
            query_params['page'] = str(page_number + 1)
            next_page = f"{base_url}?{query_params.urlencode()}"

        # Previous page
        previous_page = None
        if page_number > 1:
            query_params['page'] = str(page_number - 1)
            previous_page = f"{base_url}?{query_params.urlencode()}"

        return {
            'count': total_items,
            'next': next_page,
            'previous': previous_page,
            'results': current_page_items
        }
