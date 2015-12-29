import unittest
from unittest.mock import Mock, sentinel, patch

import pytest

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from api.models import Activity
from api.tests.factories import UserFactory
from api.views import WindDirection


class TestWindDirection(unittest.TestCase):

    @patch('api.views.json')
    @patch('api.views.HttpResponse')
    def test_get_returns_existing_wind_direction(self,
                                                 mock_http,
                                                 mock_json):
        user = UserFactory.stub()
        wind_dir = "10.0"

        class MockedGetObject(object):
            def get_object(self):
                activity = Mock()
                activity.user = UserFactory.stub()
                activity.wind_direction = wind_dir
                activity.private = False

                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        request = RequestFactory()
        request.user = user
        view = MockedWindDirection()
        view.kwargs = dict(pk=1)

        mock_json.dumps.return_value = sentinel.json_data
        mock_http.return_value = sentinel.http_response

        response = view.get(request)

        mock_json.dumps.assert_called_once_with(dict(wind_direction="10.0"))
        mock_http.assert_called_once_with(sentinel.json_data,
                                          content_type="application/json")

        self.assertEqual(response, sentinel.http_response)

    @patch('api.views.HttpResponse')
    def test_get_returns_if_private_and_cur_user(self,
                                                 mock_http):
        user = UserFactory.stub()
        wind_dir = "10.0"

        class MockedGetObject(object):
            def get_object(self):
                activity = Mock()
                activity.user = user
                activity.wind_direction = wind_dir
                activity.private = True
                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        request = RequestFactory()
        request.user = user
        view = MockedWindDirection()
        view.kwargs = dict(pk=1)

        mock_http.return_value = sentinel.http_response

        response = view.get(request)
        mock_http.assert_called_once()

        self.assertEqual(response, sentinel.http_response)

    @patch('api.views.HttpResponse')
    def test_get_raises_permission_denied_if_wrong_user_and_private(self,
                                                                    mock_http):
        user = UserFactory.stub()
        wind_dir = "10.0"

        class MockedGetObject(object):
            def get_object(self):
                activity = Mock()
                activity.user = UserFactory.stub()
                activity.wind_direction = wind_dir
                activity.private = True
                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        request = RequestFactory()
        request.user = user
        view = MockedWindDirection()
        view.kwargs = dict(pk=1)

        mock_http.return_value = sentinel.http_response

        with self.assertRaises(PermissionDenied):
            view.get(request)

    def test_post_throws_if_not_current_user(self):

        user = UserFactory.stub()
        wind_dir = "10.0"

        class MockedGetObject(object):
            def get_object(self):
                activity = Mock()
                activity.user = UserFactory.stub()
                activity.wind_direction = wind_dir
                activity.private = True
                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        request = RequestFactory()
        request.user = user
        view = MockedWindDirection()
        view.kwargs = dict(pk=1)

        with self.assertRaises(PermissionDenied):
            view.get(request)

    def test_post_saves_wind_dir(self):

        user = UserFactory.stub()
        activity = Mock()
        activity.user = user

        class MockedGetObject(object):
            def get_object(self):
                return activity

        class MockedWindDirection(MockedGetObject, WindDirection):
            pass

        request = RequestFactory()
        request.user = user
        request.POST = dict(wind_direction="10.0")
        view = MockedWindDirection()
        view.kwargs = dict(pk=1)
        view.get = Mock()

        view.post(request)

        self.assertEqual(activity.wind_direction, "10.0")
        activity.save.assert_called_once_with()
        view.get.assert_called_once_with(request)


@pytest.mark.integration
class TestDeleteActivityViewIntegration(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='test')
        self.client.login(username='test', password='password')
        Activity.objects.create(user=self.user)

    def test_delete_redirects_to_homepage(self):
        response = self.client.get(reverse('delete_activity',
                                           args=[1]))
        self.assertRedirects(response, reverse('home'))

    def test_delete_removes_item_from_db(self):
        self.client.get(reverse('delete_activity', args=[1]))
        self.assertRaises(ObjectDoesNotExist,
                          lambda: Activity.objects.get(id=1)
                          )
