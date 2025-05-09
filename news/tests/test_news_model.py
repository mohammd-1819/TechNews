import pytest

pytestmark = pytest.mark.django_db


class TestNewsModel:

    def test_news_str(self, news_factory):
        news = news_factory()

        assert news.__str__() == news.title
