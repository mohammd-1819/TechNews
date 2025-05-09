import factory
from faker import Faker
from account.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f"user_{n}")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        username = kwargs.pop('username')
        password = kwargs.pop('password', 'password')

        user = manager.create_user(username=username, password=password)

        for key, value in kwargs.items():
            setattr(user, key, value)

        user.save()
        return user

    @factory.post_generation
    def email(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.email = extracted
        else:
            self.email = f"{self.username}@example.com"
        self.save()

    @factory.post_generation
    def fullname(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.fullname = extracted
        else:
            self.fullname = fake.name()
        self.save()


class AdminFactory(UserFactory):
    username = factory.Sequence(lambda n: f"admin_{n}")

    @factory.post_generation
    def is_admin(self, create, extracted, **kwargs):
        if not create:
            return

        self.is_admin = True
        self.save()
