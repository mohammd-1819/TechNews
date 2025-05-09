import pytest
from rest_framework import status
from django.urls import reverse
from news.models.news_model import News

pytestmark = pytest.mark.django_db


class TestRemoveNewsEndpoint:
    def get_endpoint(self, news_id):
        return reverse('news:news-remove', kwargs={'news_id': news_id})

    def get_jwt_token(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access']

    def test_admin_can_remove_news(self, news_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        news = news_factory(title='News to Delete')
        news_id = news.id

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        # act
        response = client.delete(
            self.get_endpoint(news.id),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'News Removed'

    def test_non_admin_cannot_remove_news(self, news_factory, api_client, django_user_model):
        # arrange
        user_username = 'user'
        user_password = 'user_password'

        regular_user = django_user_model.objects.create_user(
            username=user_username,
            password=user_password
        )

        news = news_factory(title='News should not be deleted')
        news_id = news.id

        access_token = self.get_jwt_token(api_client, user_username, user_password)

        client = api_client()

        # act
        response = client.delete(
            self.get_endpoint(news.id),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

        assert News.objects.filter(id=news_id).exists()

    def test_unauthenticated_user_cannot_remove_news(self, news_factory, api_client):
        # arrange
        news = news_factory(title='News should not be deleted')
        news_id = news.id

        client = api_client()

        # act
        response = client.delete(self.get_endpoint(news.id))

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert News.objects.filter(id=news_id).exists()

    def test_remove_non_existent_news(self, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        non_existent_id = 'e8bc413e-2b26-49e9-a3da-e0a4ec9f1545'

        # act
        response = client.delete(
            self.get_endpoint(non_existent_id),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_remove_news_with_associated_tags(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        # ایجاد کاربر ادمین
        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        tag1 = tag_factory(name='tag1')
        tag2 = tag_factory(name='tag2')

        news = news_factory(title='News with tags')
        news.tags.add(tag1, tag2)
        news_id = news.id

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        # act
        response = client.delete(
            self.get_endpoint(news.id),
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK

        assert tag1 in tag_factory._meta.model.objects.all()
        assert tag2 in tag_factory._meta.model.objects.all()
