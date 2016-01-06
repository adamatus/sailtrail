import unittest
from unittest.mock import patch, sentinel, Mock

from homepage.views import HomePageView


class TestHomepageView(unittest.TestCase):

    def setUp(self):
        self.user = Mock()
        self.request = Mock()
        self.request.user = self.user
        view = HomePageView()
        view.request = self.request
        view.object_list = [1, 2, 3]
        view.paginate_by = 1
        view.page_kwarg = "1"
        view.kwargs = {"1": 1}
        self.view = view

    @patch('homepage.views.get_activities_for_user')
    def test_get_queryset_calls_through_to_helper(self, mock_helper: Mock):
        # Given a mock get_activities that returns a sentinel
        mock_helper.return_value = sentinel.activity_list

        # When getting the queryset for the view
        queryset = self.view.get_queryset()

        # Then the sentinel will be returned
        assert queryset == sentinel.activity_list

        # and the mock will have been called with the current user
        mock_helper.assert_called_once_with(self.user)

    @patch('homepage.views.get_leaders')
    def test_get_context_data_populates_leaders(self, mock_helper: Mock):
        # Given a mock get_leaders that returns a sentinel
        mock_helper.return_value = sentinel.leaders

        # When getting the context for the view
        context = self.view.get_context_data()

        # Then the context will contain the sentinel
        assert context['leaders'] == sentinel.leaders
