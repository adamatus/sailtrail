import unittest
from unittest.mock import MagicMock, patch, sentinel

from leaders.sitemap import LeaderboardSitemap


class TestLeaderboardSitemap(unittest.TestCase):

    def setUp(self):
        self.sitemap = LeaderboardSitemap()

    def test_items_returns_leaderboard(self):
        # When getting the items for the sitemap
        items = self.sitemap.items()

        # Then there is 1 item returned
        assert len(items) == 1
        assert items[0] == 'leaderboards'

    @patch('leaders.sitemap.reverse')
    def test_location_uses_django_reverse(self, reverse_mock: MagicMock):
        # Given a mock that returns a sentinel location
        reverse_mock.return_value = sentinel.location

        # When calculating the location for a sentinel item
        location = self.sitemap.location(sentinel.item)

        # Then the location is returned, after the helper is called
        assert location == sentinel.location
        reverse_mock.assert_called_once_with(sentinel.item)
