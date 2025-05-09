import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db


class TestLogoutEndpoint:
    endpoint = reverse('account:logout')

    def get_tokens(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access'], response.data['refresh']

    def test_successful_logout(self, api_client, user_factory):
        # arrange
        user = user_factory(username='testuser')

        access_token, refresh_token = self.get_tokens(api_client, 'testuser', 'password')

        client = api_client()

        payload = {
            'refresh_token': refresh_token
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Successfully logged out.'

        refresh_url = reverse('account:token_refresh')
        refresh_response = client.post(refresh_url, {'refresh': refresh_token})
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_token(self, api_client, user_factory):
        # arrange
        user = user_factory(username='testuser')

        access_token, _ = self.get_tokens(api_client, 'testuser', 'password')

        client = api_client()

        payload = {}

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == 'Invalid token or token not provided.'

    def test_logout_with_invalid_token(self, api_client, user_factory):
        # arrange
        user = user_factory(username='testuser')

        access_token, _ = self.get_tokens(api_client, 'testuser', 'password')

        client = api_client()

        payload = {
            'refresh_token': 'invalid_refresh_token'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
        assert response.data['error'] == 'Invalid token or token not provided.'

    def test_logout_unauthenticated_user(self, api_client):
        # arrange
        client = api_client()

        payload = {
            'refresh_token': 'some_refresh_token'
        }

        # act
        response = client.post(self.endpoint, data=payload)

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_already_blacklisted_token(self, api_client, user_factory):
        # arrange
        user = user_factory(username='testuser')

        access_token, refresh_token = self.get_tokens(api_client, 'testuser', 'password')

        client = api_client()

        first_payload = {
            'refresh_token': refresh_token
        }
        client.post(
            self.endpoint,
            data=first_payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        second_payload = {
            'refresh_token': refresh_token
        }

        # act
        response = client.post(
            self.endpoint,
            data=second_payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert 'error' in response.data

    def test_logout_with_missing_refresh_token_key(self, api_client, user_factory):
        # arrange
        user = user_factory(username='testuser')

        access_token, refresh_token = self.get_tokens(api_client, 'testuser', 'password')

        client = api_client()

        payload = {
            'wrong_key': refresh_token
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
