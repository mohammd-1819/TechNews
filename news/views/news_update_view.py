from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from news.serializers.news_ser import NewsSerializer
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema


class UpdateNewsView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = NewsSerializer

    @extend_schema(
        tags=['News'],
        summary='Update News',
        responses={200: NewsSerializer}
    )
    def put(self, request, news_id):
        news = get_object_or_404(id=news_id)
        serializer = self.serializer_class(instance=news, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'News Updated Successfully', 'result': serializer.data},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
