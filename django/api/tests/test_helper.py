import unittest
from unittest.mock import patch, sentinel, Mock

import pytest
from django.core.exceptions import PermissionDenied

from api.helper import (create_new_activity_for_user, get_activity_by_id,
                        get_activities_for_user, get_users_activities,
                        get_public_activities, verify_private_owner,
                        get_active_users, summarize_by_category,
                        _get_activity_leaders, get_leaders)
from api.models import Activity, ActivityTrack


class TestHelper(unittest.TestCase):

    def setUp(self):
        patcher = patch('api.helper.Activity')
        self.activity_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_new_activity_for_user(self):
        # Given a mock that returns an activity
        self.activity_mock.objects.create.return_value = sentinel.activity

        # When creating a new activity
        activity = create_new_activity_for_user(sentinel.user)

        # Then sentinel is returned, after correct mock call
        assert activity == sentinel.activity
        self.activity_mock.objects.create.assert_called_with(
            user=sentinel.user)

    def test_get_activity_by_id(self):
        # Given a mock that returns an activity
        self.activity_mock.objects.get.return_value = sentinel.activity

        # When getting an activity
        activity = get_activity_by_id(sentinel.id)

        # Then the sentinel is returned, after correct mock call
        assert activity == sentinel.activity
        self.activity_mock.objects.get.assert_called_with(id=sentinel.id)

    @patch('api.helper.Q')
    def test_get_activities_for_user(self, q_mock):
        # Given a mock queryset
        queryset = Mock()
        queryset.exclude.return_value = sentinel.queryset

        # and a mock method activity that returns the queryset
        self.activity_mock.objects.exclude.return_value = queryset

        # and a mock
        q_mock.return_value = 1

        # and a mock user
        user = Mock(username=sentinel.user)

        # When getting the activities
        activities = get_activities_for_user(user)

        # Then the queryset sentinel is returned, via correct mock calls
        assert activities == sentinel.queryset
        self.activity_mock.objects.exclude.assert_called_with(
            name__isnull=True
        )
        q_mock.assert_called_with(user__username=sentinel.user)
        queryset.exclude.assert_called_with(-2, private=True)

    def test_get_users_activities_for_own_user(self):
        # Given a mock user
        user = Mock(username=sentinel.user)

        # and a mock queryset
        queryset = Mock()

        # and an activity mock that returns the queryset
        self.activity_mock.objects.filter.return_value = queryset

        # When getting the users activities
        activities = get_users_activities(user, user)

        # Then the queryset sentinel is returned, via correct mock calls
        assert activities == queryset
        self.activity_mock.objects.filter.assert_called_with(
            user__username=sentinel.user
        )
        queryset.filter.assert_not_called()

    def test_get_users_activities_for_other_user(self):
        # Given two mock users
        user = Mock(username=sentinel.user)
        user2 = Mock(username=sentinel.user2)

        # and a mock queryset
        queryset = Mock()
        queryset.filter.return_value = sentinel.queryset

        # and an activity mock that returns the queryset
        self.activity_mock.objects.filter.return_value = queryset

        # When getting the users activities
        activities = get_users_activities(user, user2)

        # Then the queryset sentinel is returned, via correct mock calls
        assert activities == sentinel.queryset
        self.activity_mock.objects.filter.assert_called_with(
            user__username=sentinel.user
        )
        queryset.filter.assert_called_with(private=False)

    def test_get_public_activities(self):
        # Given a mock that returns a sentinel
        self.activity_mock.objects.filter.return_value = sentinel.queryset

        # When getting the public activities
        activities = get_public_activities()

        # Then the sentinel is returned, with correct mock calls
        assert activities == sentinel.queryset
        self.activity_mock.objects.filter.assert_called_with(
            private=False
        )

    def test_verify_private_owner_with_public_activity_other_user(self):
        # Given an public activity mock for another user
        activity = Mock(private=False, user=sentinel.other, spec=Activity)

        # and a request mock
        request = Mock(user=sentinel.user)

        # When verifying private owner
        nothing = verify_private_owner(activity, request)

        # Then nothing is returned (i.e., no exception thrown)
        assert nothing is None

    def test_verify_private_owner_with_private_activity_same_user(self):
        # Given an private activity mock for user
        activity = Mock(private=True, user=sentinel.user, spec=Activity)

        # and a request mock
        request = Mock(user=sentinel.user)

        # When verifying private owner
        nothing = verify_private_owner(activity, request)

        # Then nothing is returned (i.e., no exception thrown)
        assert nothing is None

    def test_verify_private_owner_with_private_activity_other_user(self):
        # Given a private activity mock for another user
        activity = Mock(private=True, user=sentinel.other, spec=Activity)

        # and a request mock
        request = Mock(user=sentinel.user)

        # When verifying private owner, Then a permission denied is raised
        with pytest.raises(PermissionDenied):
            verify_private_owner(activity, request)

    def test_verify_private_owner_with_private_track_other_user(self):
        # Given a private track and activity mock for another user
        activity = Mock(private=True, user=sentinel.other, spec=Activity)
        track = Mock(spec=ActivityTrack, activity=activity)

        # and a request mock
        request = Mock(user=sentinel.user)

        # When verifying private owner, Then a permission denied is raised
        with pytest.raises(PermissionDenied):
            verify_private_owner(track, request)

    @patch('api.helper.User')
    def test_get_active_users(self, user_mock):
        # Given a user mock that returns a sentinel
        user_mock.objects.filter.return_value = sentinel.queryset

        # When getting active users
        queryset = get_active_users()

        # Then the sentinel is returned, after correct mock call
        assert queryset == sentinel.queryset
        user_mock.objects.filter.assert_called_once_with(is_active=True,
                                                         is_superuser=False)

    @patch('api.helper._get_activity_leaders')
    def test_get_leaders(self, mock_private):
        # Given a mock private helper that returns mock data, which include
        # an entry that should not appear in the output (XX)
        mock_private.return_value = [dict(category='WS', other=sentinel.a),
                                     dict(category='WS', other=sentinel.b),
                                     dict(category='SL', other=sentinel.c),
                                     dict(category='XX', other=sentinel.d)]

        # When getting the leaders
        leaders = get_leaders()

        # Then the correct list is returned
        assert len(leaders) == 2
        assert leaders[0]['category'] == 'Sailing'
        assert leaders[0]['leaders'] == [dict(category='SL', other=sentinel.c)]
        assert leaders[1]['category'] == 'Windsurfing'
        assert len(leaders[1]['leaders']) == 2
        assert leaders[1]['leaders'][0] == dict(category='WS',
                                                other=sentinel.a)
        assert leaders[1]['leaders'][1] == dict(category='WS',
                                                other=sentinel.b)

    @patch('api.helper.Max')
    def test_private_get_activity_leaders(self, max_mock):
        # Given a set of mocks for the chained calls
        activity = self.activity_mock
        filter = activity.objects.filter
        values = filter.return_value.values
        annotate = values.return_value.annotate
        order_by = annotate.return_value.order_by
        order_by.return_value = sentinel.queryset
        max_mock.return_value = sentinel.max

        # When getting the activity leaders
        leaders = _get_activity_leaders()

        # Then the sentinel is returned, and mocks called correctly
        assert leaders == sentinel.queryset
        filter.assert_called_with(private=False)
        values.assert_called_with('user__username', 'category')
        annotate.assert_called_with(max_speed=sentinel.max)
        max_mock.assert_called_with('model_max_speed')
        order_by.assert_called_with('-max_speed')

    @patch('api.helper.Count')
    @patch('api.helper.Max')
    @patch('api.helper.Sum')
    def test_summarize_by_category(self, mock_sum, mock_max, mock_count):
        # Given a values mock returned by the activity mock
        activities = Mock()
        activities.values.return_value.annotate\
            .return_value.order_by.return_value = sentinel.queryset
        mock_sum.return_value = sentinel.sum
        mock_max.return_value = sentinel.max
        mock_count.return_value = sentinel.count

        # When summarizing by category
        queryset = summarize_by_category(activities)

        # Then the sentinel queryset is returned, and mocks called as expected
        assert queryset == sentinel.queryset
        activities.values.assert_called_with('category')
        mock_sum.assert_called_with('model_distance')
        mock_max.assert_called_with('model_max_speed')
        mock_count.assert_called_with('category')
        activities.values.return_value.annotate.assert_called_with(
            count=sentinel.count,
            max_speed=sentinel.max,
            total_dist=sentinel.sum
        )
        activities.values.return_value.annotate.return_value.order_by\
            .assert_called_with('-max_speed')
