from datetime import datetime
from math import floor

import factory
from django.contrib.auth import get_user_model
from factory.fuzzy import FuzzyFloat

from api.models import (Activity, ActivityTrack,
                        ActivityTrackpoint)

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
    name = None
    description = None
    category = 'SL'


class ActivityTrackFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityTrack

    original_filename = factory.Sequence(lambda n: 'testuser%s.sbn' % n)
    trimmed = False
    activity_id = factory.SubFactory(ActivityFactory)


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
    track_id = factory.SubFactory(ActivityTrackFactory)
