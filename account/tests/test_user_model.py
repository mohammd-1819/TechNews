import pytest
from django.contrib.auth import get_user_model
from .factory import UserFactory, AdminFactory

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestUserModel:

    def test_create_user(self):
        # arrange & act
        user = User.objects.create_user(
            username="testuser",
            password="securepassword123"
        )
        user.email = "testuser@example.com"
        user.fullname = "Test User"
        user.save()

        # assert
        assert user.username == "testuser"
        assert user.email == "testuser@example.com"
        assert user.fullname == "Test User"
        assert user.is_active is True
        assert user.is_admin is False
        assert user.is_staff is False
        assert user.check_password("securepassword123") is True
        assert str(user) == "testuser"

    def test_create_admin(self):
        # arrange & act
        admin = User.objects.create_superuser(
            username="adminuser",
            password="adminpassword123"
        )
        admin.email = "admin@example.com"
        admin.fullname = "Admin User"
        admin.save()

        # assert
        assert admin.username == "adminuser"
        assert admin.email == "admin@example.com"
        assert admin.fullname == "Admin User"
        assert admin.is_active is True
        assert admin.is_admin is True
        assert admin.is_staff is True  # property based on is_admin
        assert admin.check_password("adminpassword123") is True