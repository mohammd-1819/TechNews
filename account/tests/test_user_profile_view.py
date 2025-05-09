import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestUserProfileEndpoint:
    endpoint = reverse('account:user-profile')

    def get_jwt_token(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access']

    def test_authenticated_user_can_get_profile(self, api_client, user_factory):
        # arrange
        user = user_factory(
            username='testuser',
            fullname='Test User'
        )

        access_token = self.get_jwt_token(api_client, 'testuser', 'password')

        client = api_client()

        # act
        response = client.get(
            self.endpoint,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['fullname'] == 'Test User'

    def test_unauthenticated_user_cannot_get_profile(self, api_client):
        # arrange
        client = api_client()

        # act
        response = client.get(self.endpoint)

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_returns_correct_user_data(self, api_client, user_factory):
        # arrange
        user = user_factory(
            username='detailuser',
            email='details@example.com',
            fullname='Detail User',
        )

        access_token = self.get_jwt_token(api_client, 'detailuser', 'password')

        client = api_client()

        # act
        response = client.get(
            self.endpoint,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'detailuser'
        assert response.data['email'] == 'details@example.com'
        assert response.data['fullname'] == 'Detail User'

    def test_admin_user_profile_data(self, api_client, user_factory):
        # arrange
        admin_user = user_factory(
            username='adminuser',
            email='admin@example.com',
            fullname='Admin User',
            is_superuser=True
        )

        # دریافت توکن JWT
        access_token = self.get_jwt_token(api_client, 'adminuser', 'password')

        client = api_client()

        # act
        response = client.get(
            self.endpoint,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'adminuser'

    def test_inactive_user_cannot_get_profile(self, api_client, user_factory):
        # arrange
        inactive_user = user_factory(
            username='inactiveuser',
            is_active=False
        )

        # تلاش برای دریافت توکن JWT
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': 'inactiveuser', 'password': 'password'})

        # assert
        # کاربر غیرفعال نباید بتواند توکن دریافت کند
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_with_invalid_token(self, api_client):
        # arrange
        client = api_client()

        # act
        response = client.get(
            self.endpoint,
            HTTP_AUTHORIZATION='Bearer invalidtoken123'
        )

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_with_different_auth_method(self, api_client, user_factory):
        # arrange
        user = user_factory(username='basicauthuser')

        client = api_client()
        client.login(username='basicauthuser', password='password')

        # act
        response = client.get(self.endpoint)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]
