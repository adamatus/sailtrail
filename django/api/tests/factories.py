from datetime import datetime
from math import floor

from pytz import utc

import factory
from factory.fuzzy import FuzzyFloat

from api.models import (Activity, ActivityTrack,
                        ActivityTrackpoint)
from users.tests.factories import UserFactory


class ActivityFactory(factory.DjangoModelFactory):

    class Meta:
        model = Activity

    user = factory.SubFactory(UserFactory)
    distance = None
    max_speed = None
    name = None
    description = None
    category = 'SL'


class ActivityTrackFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityTrack

    original_filename = factory.Sequence(lambda n: 'testuser%s.sbn' % n)
    trimmed = False
    activity = factory.SubFactory(ActivityFactory)


class ActivityTrackpointFactory(factory.DjangoModelFactory):

    class Meta:
        model = ActivityTrackpoint

    timepoint = factory.Sequence(
        lambda n:
            datetime(2014, 10, 10, floor(n / (60**2)),
                     floor(n / 60), n % 60, tzinfo=utc))
    lat = FuzzyFloat(-180, 180)
    lon = FuzzyFloat(-180, 180)  # degrees
    sog = FuzzyFloat(0, 20)
    track = factory.SubFactory(ActivityTrackFactory)
