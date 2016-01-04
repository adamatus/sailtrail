from unittest.mock import MagicMock, patch, sentinel

from leaders.sitemap import LeaderboardSitemap


class TestLeaderboardSitemap:

    def test_items_returns_leaderboard(self):
        sitemap = LeaderboardSitemap()

        items = sitemap.items()

        assert len(items) == 1
        assert items[0] == 'leaderboards'

    @patch('leaders.sitemap.reverse')
    def test_location_uses_django_reverse(self, reverse_mock: MagicMock):
        sitemap = LeaderboardSitemap()

        reverse_mock.return_value = sentinel.location

        location = sitemap.location(sentinel.item)

        assert location == sentinel.location
        reverse_mock.assert_called_once_with(sentinel.item)
