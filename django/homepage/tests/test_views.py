from unittest.mock import patch, sentinel, Mock

from homepage.views import HomePageView


class TestHomepageView:

    @patch('homepage.views.get_activities_for_user')
    def test_get_queryset_calls_through_to_helper(self, mock_helper: Mock):
        # Given a mock get_activities that returns a sentinel
        mock_helper.return_value = sentinel.activity_list

        view = HomePageView()
        view.request = Mock(user=sentinel.user)

        # When getting the queryset for the view
        queryset = view.get_queryset()

        # Then the sentinel will be returned
        assert queryset == sentinel.activity_list

        # and the mock will have been called with the current user
        mock_helper.assert_called_once_with(sentinel.user)

    @patch('homepage.views.get_leaders')
    @patch('homepage.views.ListView.get_context_data')
    def test_get_context_data_populates_leaders(self,
                                                get_context_mock: Mock,
                                                get_leaders_mock: Mock):
        # Given a mock get_leaders that returns a sentinel
        get_leaders_mock.return_value = sentinel.leaders

        get_context_mock.return_value = dict(super=sentinel.super)

        view = HomePageView()

        # When getting the context for the view
        context = view.get_context_data()

        # Then the context will contain the sentinel
        assert context['leaders'] == sentinel.leaders
        assert context['super'] == sentinel.super
