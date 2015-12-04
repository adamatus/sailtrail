import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'testuser%s' % n)
    email = factory.Sequence(lambda n: 'email%s@example.com' % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')
