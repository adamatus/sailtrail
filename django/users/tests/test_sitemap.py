import unittest
from unittest.mock import MagicMock, patch, sentinel, Mock

from users.sitemap import UsersSitemap


class TestUsersSitemap(unittest.TestCase):

    def setUp(self):
        self.sitemap = UsersSitemap()

    @patch('users.sitemap.get_active_users')
    def test_items_returns_helper_result(self, helper_mock: MagicMock):
        # Given a mock helper that returns a sentinel
        helper_mock.return_value = sentinel.user_list

        # When getting items for the sitemap
        items = self.sitemap.items()

        # Then the sentinel is returned
        assert items == sentinel.user_list

    @patch('users.sitemap.reverse')
    def test_location_uses_reverse(self, reverse_mock: MagicMock):
        # Given a mock helper that returns a location
        reverse_mock.return_value = sentinel.location

        # and a mock user
        user = Mock(username=sentinel.username)

        # When getting the sitemap location for the user
        location = self.sitemap.location(user)

        # Then the sentinel is returned, after the helper is called
        assert location == sentinel.location
        reverse_mock.assert_called_once_with('users:user',
                                             args=['sentinel.username'])
