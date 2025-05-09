from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


class CreateNewsView(APIView):
    """
    API view to create new news articles.

    This view allows administrators to create new news articles.
    Only users with admin privileges can access this endpoint.
    """
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        operation_id='create_news',
        summary='Create a new news article',
        description='''
        This endpoint allows administrators to create new news articles.

        **Features**:
        - Create news articles with title, text, source, and tags
        - Automatic validation of input data
        - Only accessible to admin users

        **Authentication**:
        - Requires valid admin authentication token
        - Returns 401 if user is not authenticated
        - Returns 403 if user is not an administrator
        ''',
        request=NewsSerializer,
        responses={
            201: OpenApiResponse(
                response=NewsSerializer,
                description='News article created successfully',
                examples=[
                    OpenApiExample(
                        'Successful Response',
                        value={
                            "message": "News Created Successfully",
                            "result": {
                                "id": "e8bc413e-2b26-49e9-a3da-e0a4dc9f3568",
                                "title": "New Article Title",
                                "text": "Article content goes here",
                                "source": "Reliable Source",
                                "created_at": "2025-05-08T17:44:10.279522Z",
                                "updated_at": "2025-05-08T17:44:10.279522Z",
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
                            "title": ["This field is required."],
                            "text": ["This field is required."]
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
                        value={'detail': 'Authentication credentials were not provided.'},
                        response_only=True
                    )
                ]
            ),
            403: OpenApiResponse(
                description='User does not have admin privileges',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'detail': 'You do not have permission to perform this action.'},
                        response_only=True
                    )
                ]
            )
        },
        examples=[
            OpenApiExample(
                'Sample Request',
                value={
                    "title": "string",
                    "text": "string",
                    "source": "string",
                    "tags": [
                        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                    ]
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """
        Create a new news article.

        Args:
            request: HTTP request object containing news article data

        Returns:
            Response: Created news article data with HTTP 201 status or error details

        Raises:
            ValidationError: If the provided data is invalid
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'News Created Successfully', 'result': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


