import factory
from factory.fuzzy import FuzzyFloat

from math import floor

from activities.models import (Activity, ActivityTrack, ActivityDetail,
                               ActivityTrackpoint)
from django.contrib.auth import get_user_model

from datetime import datetime

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'testuser%s' % n)
    email = factory.Sequence(lambda n: 'email%s@example.com' % n)
    password = factory.PostGenerationMethodCall('set_password', 'password')


class ActivityFactory(factory.DjangoModelFactory):

    class Meta:
        model = Activity

    user = factory.SubFactory(UserFactory)
    model_distance = None
    model_max_speed = None


class ActivityTrackFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityTrack

    original_filename = factory.Sequence(lambda n: 'testuser%s.sbn' % n)
    trimmed = False
    activity_id = factory.SubFactory(ActivityFactory)


class ActivityDetailFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityDetail

    name = factory.Sequence(lambda n: 'Activity name %s' % n)
    description = factory.Sequence(lambda n: 'Activity description %s' % n)
    activity_id = factory.SubFactory(ActivityFactory)
    category = 'SL'


class ActivityTrackpointFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityTrackpoint

    timepoint = factory.Sequence(
        lambda n:
            datetime(2014, 10, 10, floor(n / (60**3)),
                     floor(n / (60**2)), floor(n / 60)))
    lat = FuzzyFloat(-180, 180)
    lon = FuzzyFloat(-180, 180)  # degrees
    sog = FuzzyFloat(0, 20)
