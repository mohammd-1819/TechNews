import pytest

pytestmark = pytest.mark.django_db


class TestNewsModel:

    def test_tag_str(self, tag_factory):
        tag = tag_factory()

        assert tag.__str__() == tag.name
