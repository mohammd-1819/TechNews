import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestUpdateProfileEndpoint:
    endpoint = reverse('account:update-user-profile')

    def get_jwt_token(self, api_client, username, password):
        token_url = reverse('account:token_obtain_pair')
        response = api_client().post(token_url, {'username': username, 'password': password})
        return response.data['access']

    def test_authenticated_user_can_update_profile(self, api_client, user_factory):
        # arrange
        user = user_factory(
            username='testuser',
            email='old@example.com',
            fullname='Old Name'
        )

        access_token = self.get_jwt_token(api_client, 'testuser', 'password')

        client = api_client()

        payload = {
            'email': 'new@example.com',
            'fullname': 'New Name'
        }

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Profile Updated'
        assert response.data['result']['email'] == 'new@example.com'
        assert response.data['result']['fullname'] == 'New Name'
        assert response.data['result']['username'] == 'testuser'

    def test_unauthenticated_user_cannot_update_profile(self, api_client):
        # arrange
        client = api_client()

        payload = {
            'email': 'new@example.com',
            'fullname': 'New Name'
        }

        # act
        response = client.put(self.endpoint, data=payload)

        # assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_username_to_existing_one(self, api_client, user_factory):
        # arrange

        user1 = user_factory(username='user1')
        user2 = user_factory(username='user2')

        access_token = self.get_jwt_token(api_client, 'user1', 'password')

        client = api_client()

        payload = {
            'username': 'user2'
        }

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_partial_update_keeps_other_fields(self, api_client, user_factory, django_user_model):
        # arrange
        user = user_factory(
            username='completeuser',
            email='complete@example.com',
            fullname='Complete User'
        )

        access_token = self.get_jwt_token(api_client, 'completeuser', 'password')

        client = api_client()

        payload = {
            'email': 'updated@example.com'
        }

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['email'] == 'updated@example.com'
        assert response.data['result']['fullname'] == 'Complete User'

        updated_user = django_user_model.objects.get(username='completeuser')
        assert updated_user.email == 'updated@example.com'
        assert updated_user.fullname == 'Complete User'

    def test_update_multiple_fields(self, api_client, user_factory):
        # arrange
        user = user_factory(
            username='multiuser',
            email='multi@example.com',
            fullname='Multi User'
        )

        access_token = self.get_jwt_token(api_client, 'multiuser', 'password')

        client = api_client()

        payload = {
            'email': 'multi-updated@example.com',
            'fullname': 'Updated Multi User'
        }

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['email'] == 'multi-updated@example.com'
        assert response.data['result']['fullname'] == 'Updated Multi User'

    def test_update_profile_with_empty_data(self, api_client, user_factory):
        # arrange
        user = user_factory(
            username='emptyuser',
            email='empty@example.com',
            fullname='Empty User'
        )

        access_token = self.get_jwt_token(api_client, 'emptyuser', 'password')

        client = api_client()

        # ارسال داده‌ی خالی
        payload = {}

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['email'] == 'empty@example.com'
        assert response.data['result']['fullname'] == 'Empty User'

    def test_admin_user_can_update_own_profile(self, api_client, admin_factory):
        # arrange
        admin_user = admin_factory(
            username='adminuser',
            email='admin@example.com',
        )

        access_token = self.get_jwt_token(api_client, 'adminuser', 'password')

        client = api_client()

        payload = {
            'email': 'admin-updated@example.com'
        }

        # act
        response = client.put(
            self.endpoint,
            data=payload,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        # assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['result']['email'] == 'admin-updated@example.com'
