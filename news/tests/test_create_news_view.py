import pytest
from rest_framework import status
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestCreateNewsEndpoint:
    endpoint = reverse('news:news-create')

    def get_jwt_token(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access']

    def test_admin_can_create_news(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        # ایجاد کاربر ادمین
        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()
        tag = tag_factory()

        payload = {
            'title': 'Test News Title',
            'text': 'Test news content',
            'source': 'awdawdadwawd',
            'tags': tag.id

        }

        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'News Created Successfully'
        assert response.data['result']['title'] == 'Test News Title'
        assert response.data['result']['text'] == 'Test news content'

    def test_non_admin_cannot_create_news(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        user_username = 'user'
        user_password = 'user_password'

        # ایجاد کاربر عادی
        regular_user = django_user_model.objects.create_user(
            username=user_username,
            password=user_password
        )

        # دریافت توکن JWT
        access_token = self.get_jwt_token(api_client, user_username, user_password)

        client = api_client()
        tag = tag_factory()

        payload = {
            'title': 'Test News Title',
            'text': 'awdadawd',
            'source': 'awdawdadwawd',
            'tags': tag.id

        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_news(self, news_factory, tag_factory, api_client):
        # arrange
        client = api_client()
        tag = tag_factory()

        payload = {
            'title': 'Test News Title',
            'text': 'awdadawd',
            'source': 'awdawdadwawd',
            'tags': tag.id

        }
        # act
        response = client.post(self.endpoint, data=payload)

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_data_returns_400(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()
        tag = tag_factory()

        payload = {
            'text': 'awdadawd',
            'source': 'awdawdadwawd',
            'tags': tag.id

        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data

    def test_create_news_with_tags(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        # ایجاد کاربر ادمین
        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        # دریافت توکن JWT
        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        tag1 = tag_factory(name='technology')
        tag2 = tag_factory(name='science')

        client = api_client()

        payload = {
            'title': 'Test News with Tags',
            'text': 'awdadawd',
            'source': 'awdawdadwawd',
            'tags': [tag1.id, tag2.id]
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['result']['title'] == 'Test News with Tags'
