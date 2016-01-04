import unittest
from unittest.mock import patch, MagicMock, sentinel

from leaders.views import LeaderboardView


class TestLeaderboardViewIntegration(unittest.TestCase):

    def setUp(self):
        self.view = LeaderboardView()

    @patch('leaders.views.get_leaders')
    def test_get_context_data_calls_helper(self, helper: MagicMock):
        helper.return_value = sentinel.leaders

        context = self.view.get_context_data()

        assert context['leaders'] == sentinel.leaders
        helper.assert_called_once_with()
