import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient
from .factory import UserFactory, AdminFactory

register(UserFactory)
register(AdminFactory)


@pytest.fixture
def api_client():
    return APIClient
