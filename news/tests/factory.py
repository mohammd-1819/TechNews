import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient
