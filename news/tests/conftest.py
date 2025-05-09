import pytest
from pytest_factoryboy import register
from .factory import NewsFactory, TagFactory
from rest_framework.test import APIClient

register(NewsFactory)
register(TagFactory)


@pytest.fixture
def api_client():
    return APIClient
