import pytest
from django.urls import reverse
from rest_framework import status


pytestmark = pytest.mark.django_db


class TestNewsEndpoint:
    endpoint = reverse('news:news-list')

    def test_news_list(self, news_factory, tag_factory, api_client):
        # arrange
        tag1 = tag_factory(name='technology')
        tag2 = tag_factory(name='sport')
        news1 = news_factory(title='Tech News', tags=[tag1])
        news2 = news_factory(title='Sport News', tags=[tag2])
        news3 = news_factory(title='General News')

        # act
        response = api_client().get(self.endpoint)

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3

    def test_filter_by_single_tag(self, news_factory, tag_factory, api_client):
        # arrange
        tag = tag_factory(name='test')
        news = news_factory(title='News with Tag')
        news.tags.add(tag)  # اضافه کردن تگ به صورت صریح
        news_factory(title='News without Tag')  # خبر بدون تگ

        # act
        response = api_client().get(f"{self.endpoint}?tags=test")

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'News with Tag'

    def test_filter_by_keyword(self, news_factory, api_client):
        # arrange
        news_factory(title='Python News', text='Python is awesome')
        news_factory(title='Other News', text='Some other content')

        # act
        response = api_client().get(f"{self.endpoint}?keyword=Python")

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert 'Python' in response.data['results'][0]['title']

    def test_exclude_keyword(self, news_factory, api_client):
        # arrange
        news_factory(title='Python News', text='Python is awesome')
        news_factory(title='Java News', text='Java is great')

        # act
        response = api_client().get(f"{self.endpoint}?exclude_keyword=Python")

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert 'Java' in response.data['results'][0]['title']

    def test_ordering(self, news_factory, api_client):
        # arrange
        news_factory.create_batch(3)

        # act
        response = api_client().get(f"{self.endpoint}?ordering=-created_at")

        # assert
        assert response.status_code == status.HTTP_200_OK
        created_dates = [item['created_at'] for item in response.data['results']]
        assert created_dates == sorted(created_dates, reverse=True)
