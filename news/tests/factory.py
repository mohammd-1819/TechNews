import factory
import uuid
from factory.django import DjangoModelFactory
from datetime import datetime
from news.models.news_model import News
from news.models.tag_model import Tag


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f'tag-{n}')


class NewsFactory(DjangoModelFactory):
    class Meta:
        model = News
        skip_postgeneration_save = True

    id = factory.LazyFunction(uuid.uuid4)
    title = factory.Faker('sentence', nb_words=6)
    text = factory.Faker('paragraph', nb_sentences=5)
    source = factory.Faker('company')
    created_at = factory.LazyFunction(datetime.now)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        self.tags.add(TagFactory())
