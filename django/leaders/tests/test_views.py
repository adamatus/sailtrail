from unittest.mock import patch, MagicMock, sentinel

from leaders.views import LeaderboardView


class TestLeaderboardView:

    @patch('leaders.views.get_leaders')
    @patch('leaders.views.TemplateView.get_context_data')
    def test_get_context_data_calls_helper(self,
                                           get_context_mock: MagicMock,
                                           get_leaders_mock: MagicMock):
        # Given a mock that returns a sentinel
        get_leaders_mock.return_value = sentinel.leaders
        get_context_mock.return_value = dict(super=sentinel.super)

        # When getting the context data for a new view
        view = LeaderboardView()
        context = view.get_context_data()

        # Then the context includes the sentinel
        assert context['leaders'] == sentinel.leaders
        assert context['super'] == sentinel.super
