import unittest
from unittest.mock import patch, sentinel

from django.test import RequestFactory

from homepage.views import HomePageView
from users.tests.factories import UserFactory


class TestHomepageView(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory.stub()
        self.request = RequestFactory()
        self.request.user = self.user
        view = HomePageView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('homepage.views.get_activities_for_user')
    def test_get_queryset_calls_through_to_helper(self, mock_helper):

        mock_helper.return_value = sentinel.activity_list

        queryset = self.view.get_queryset()

        mock_helper.assert_called_once_with(self.user)

        self.assertEqual(queryset, sentinel.activity_list)

    @patch('homepage.views.get_leaders')
    def test_get_context_data_populates_leaders(self, mock_helper):

        mock_helper.return_value = sentinel.leaders

        context = self.view.get_context_data()

        mock_helper.assert_called_once_with()

        self.assertEqual(context['leaders'], sentinel.leaders)
