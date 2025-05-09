import pytest
from rest_framework import status
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestUpdateNewsEndpoint:
    def get_endpoint(self, news_id):
        return reverse('news:news-update', kwargs={'news_id': news_id})

    def get_jwt_token(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access']

    def test_admin_can_update_news(self, news_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        news = news_factory(title='Original Title')

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        payload = {
            'title': 'Updated Title',
            'text': 'Updated Text'
        }

        # act
        response = client.put(
            self.get_endpoint(news.id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'News Updated Successfully'
        assert response.data['result']['title'] == 'Updated Title'
        assert response.data['result']['text'] == 'Updated Text'

        news.refresh_from_db()
        assert news.title == 'Updated Title'
        assert news.text == 'Updated Text'

    def test_partial_update_news(self, news_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        news = news_factory(title='Original Title', text='Original text')

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        payload = {
            'title': 'Only Title Updated'
        }

        # act
        response = client.put(
            self.get_endpoint(news.id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['title'] == 'Only Title Updated'
        assert response.data['result']['text'] == 'Original text'

        news.refresh_from_db()
        assert news.title == 'Only Title Updated'
        assert news.text == 'Original text'

    def test_update_news_with_tags(self, news_factory, tag_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        old_tag = tag_factory(name='old-tag')
        new_tag1 = tag_factory(name='new-tag1')
        new_tag2 = tag_factory(name='new-tag2')

        news = news_factory(title='Original Title')
        news.tags.add(old_tag)

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        payload = {
            'title': 'Updated with New Tags',
            'tags': [new_tag1.id, new_tag2.id]
        }

        # act
        response = client.put(
            self.get_endpoint(news.id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['title'] == 'Updated with New Tags'

        news.refresh_from_db()
        assert news.tags.count() == 2
        assert new_tag1 in news.tags.all()
        assert new_tag2 in news.tags.all()
        assert old_tag not in news.tags.all()

    def test_non_admin_cannot_update_news(self, news_factory, api_client, django_user_model):
        # arrange
        user_username = 'user'
        user_password = 'user_password'

        regular_user = django_user_model.objects.create_user(
            username=user_username,
            password=user_password
        )

        news = news_factory(title='Original Title')

        access_token = self.get_jwt_token(api_client, user_username, user_password)

        client = api_client()

        payload = {
            'title': 'Attempt to Update'
        }

        # act
        response = client.put(
            self.get_endpoint(news.id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

        news.refresh_from_db()
        assert news.title == 'Original Title'

    def test_unauthenticated_user_cannot_update_news(self, news_factory, api_client):
        # arrange
        news = news_factory(title='Original Title')

        client = api_client()

        payload = {
            'title': 'Attempt to Update'
        }

        response = client.put(self.get_endpoint(news.id), data=payload)

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        news.refresh_from_db()
        assert news.title == 'Original Title'

    def test_update_non_existent_news(self, api_client, django_user_model):
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

        payload = {
            'title': 'Update Non-existent'
        }

        # act
        response = client.put(
            self.get_endpoint(non_existent_id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_data_returns_400(self, news_factory, api_client, django_user_model):
        # arrange
        admin_username = 'admin'
        admin_password = 'admin_password'

        admin_user = django_user_model.objects.create_superuser(
            username=admin_username,
            password=admin_password
        )

        news = news_factory()

        access_token = self.get_jwt_token(api_client, admin_username, admin_password)

        client = api_client()

        payload = {
            'title': ''
        }

        # act
        response = client.put(
            self.get_endpoint(news.id),
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data
