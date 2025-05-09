from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from news.models.news_model import News
from rest_framework.views import APIView
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter


class UpdateNewsView(APIView):
    """
    API view to update existing news articles.

    This view allows administrators to modify the details of existing news articles.
    Only users with admin privileges can access this endpoint.
    """
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        operation_id='update_news',
        summary='Update an existing news article',
        description='''
        This endpoint allows administrators to update an existing news article by its ID.

        **Features**:
        - Update title, text, source, and tags of existing news articles
        - Partial updates supported (only send fields that need to be changed)
        - Automatic validation of input data
        - Only accessible to admin users

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
                description='UUID of the news article to update',
                required=True
            )
        ],
        request=NewsSerializer,
        responses={
            200: OpenApiResponse(
                response=NewsSerializer,
                description='News article updated successfully',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value={
                            "message": "News Updated Successfully",
                            "result": {
                                "id": "e8bc413e-2b26-49e9-a3da-e0a4dc9f3568",
                                "title": "Updated Article Title",
                                "text": "Updated article content",
                                "source": "Updated Source",
                                "created_at": "2025-05-08T17:44:10.279522Z",
                                "updated_at": "2025-05-09T12:30:45.123456Z",
                                "tags": [
                                    "e34f422a-19a3-4ae6-a998-1254612f5e4a"
                                ]
                            }
                        },
                        response_only=True
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid input data',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        value={
                            "title": ["This field cannot be blank."],
                            "tags": ["Invalid tag ID format."]
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
        },
        examples=[
            OpenApiExample(
                'Sample Update Request',
                value={
                    "title": "Updated Title",
                    "text": "Updated content text",
                    "source": "Updated source",
                    "tags": [
                        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                    ]
                },
                request_only=True
            ),
            OpenApiExample(
                'Partial Update Request',
                value={
                    "title": "Only Update Title"
                },
                request_only=True
            )
        ]
    )
    def put(self, request, news_id):
        """
        Update an existing news article.

        Args:
            request: HTTP request object containing updated news data
            news_id: UUID of the news article to update

        Returns:
            Response: Updated news article data with HTTP 200 status or error details

        Raises:
            Http404: If the news article doesn't exist
            ValidationError: If the provided data is invalid
        """
        news = get_object_or_404(News, id=news_id)
        serializer = self.serializer_class(instance=news, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'News Updated Successfully', 'result': serializer.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

