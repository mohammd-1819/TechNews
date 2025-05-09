from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from news.models.news_model import News
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter


class RemoveNewsView(APIView):
    """
    API view to delete existing news articles.

    This view allows administrators to remove news articles from the system.
    Only users with admin privileges can access this endpoint.
    """
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        operation_id='remove_news',
        summary='Delete a news article',
        description='''
        This endpoint allows administrators to delete an existing news article by its ID.

        **Features**:
        - Permanently removes news article from the database
        - Requires admin privileges
        - Returns 404 if article doesn't exist

        **Authentication**:
        - Requires valid admin authentication token
        - Returns 401 if user is not authenticated
        - Returns 403 if user is not an administrator
        ''',
        parameters=[
            OpenApiParameter(
                name='news_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the news article to delete',
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='News article successfully deleted',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value={
                            "message": "News Removed"
                        },
                        response_only=True
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Authentication credentials were not provided',
                examples=[
                    OpenApiExample(
                        'Unauthorized',
                        value={
                            "detail": "Authentication credentials were not provided."
                        },
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description='User does not have admin privileges',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={
                            "detail": "You do not have permission to perform this action."
                        },
                        response_only=True
                    )
                ]
            ),
            404: OpenApiResponse(
                description='News article not found',
                examples=[
                    OpenApiExample(
                        'Not Found',
                        value={
                            "detail": "Not found."
                        },
                        response_only=True
                    )
                ]
            )
        }
    )
    def delete(self, request, news_id):
        """
        Delete a specific news article.

        Args:
            request: HTTP request object
            news_id: UUID of the news article to delete

        Returns:
            Response: Success message with HTTP 200 status

        Raises:
            Http404: If the news article doesn't exist
        """
        news = get_object_or_404(News, id=news_id)
        news.delete()

        return Response({'message': 'News Removed'}, status=status.HTTP_200_OK)

