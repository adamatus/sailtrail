from unittest.mock import patch, MagicMock, sentinel

from leaders.views import LeaderboardView


class TestLeaderboardView:

    @patch('leaders.views.get_leaders')
    def test_get_context_data_calls_helper(self, helper: MagicMock):
        # Given a mock that returns a sentinel
        helper.return_value = sentinel.leaders

        # When getting the context data for a new view
        view = LeaderboardView()
        context = view.get_context_data()

        # Then the context includes the sentinel
        assert context['leaders'] == sentinel.leaders
