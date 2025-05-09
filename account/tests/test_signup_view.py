import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestSignUpEndpoint:
    endpoint = reverse('account:sign-up')

    def test_user_can_signup_successfully(self, api_client):
        # arrange
        client = api_client()
        payload = {
            'username': 'testuser',
            'password': 'SecurePassword123',
            'email': 'test@example.com',
            'fullname': 'Test User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload
        )

        # assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Signup Successful'
        assert 'access_token' in response.data
        assert 'refresh_token' in response.data



    def test_user_signup_with_duplicate_username(self, api_client, user_factory):
        # arrange
        existing_user = user_factory(username='existinguser')

        client = api_client()
        payload = {
            'username': 'existinguser',
            'password': 'SecurePassword123',
            'email': 'new@example.com',
            'fullname': 'New User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_user_signup_with_short_password(self, api_client):
        # arrange
        client = api_client()
        payload = {
            'username': 'testuser',
            'password': '123',
            'email': 'test@example.com',
            'fullname': 'Test User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_user_signup_with_invalid_email(self, api_client):
        # arrange
        client = api_client()
        payload = {
            'username': 'testuser',
            'password': 'SecurePassword123',
            'email': 'invalid-email',
            'fullname': 'Test User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_authenticated_user_can_signup_another_user(self, api_client, user_factory):
        # arrange
        existing_user = user_factory(username='existinguser')

        token_url = reverse('account:token_obtain_pair')
        token_response = api_client().post(token_url, {'username': 'existinguser', 'password': 'password'})
        access_token = token_response.data['access']

        client = api_client()
        payload = {
            'username': 'newuser',
            'password': 'SecurePassword123',
            'email': 'newuser@example.com',
            'fullname': 'New User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Signup Successful'

    def test_signup_creates_user_in_database(self, api_client, django_user_model):
        # arrange
        client = api_client()
        payload = {
            'username': 'databaseuser',
            'password': 'SecurePassword123',
            'email': 'db@example.com',
            'fullname': 'Database User'
        }

        # act
        response = client.post(
            self.endpoint,
            data=payload
        )

        # assert
        assert response.status_code == status.HTTP_201_CREATED

        user = django_user_model.objects.filter(username='databaseuser').first()
        assert user is not None
        assert user.email == 'db@example.com'
        assert user.fullname == 'Database User'
        assert user.check_password('SecurePassword123')

    def test_user_can_login_after_signup(self, api_client):
        # arrange

        signup_payload = {
            'username': 'loginuser',
            'password': 'SecurePassword123',
            'email': 'login@example.com',
            'fullname': 'Login User'
        }

        signup_response = api_client().post(
            self.endpoint,
            data=signup_payload
        )

        assert signup_response.status_code == status.HTTP_201_CREATED

        token_url = reverse('account:token_obtain_pair')
        login_payload = {
            'username': 'loginuser',
            'password': 'SecurePassword123'
        }

        # act
        login_response = api_client().post(token_url, login_payload)

        # assert
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access' in login_response.data
        assert 'refresh' in login_response.data
