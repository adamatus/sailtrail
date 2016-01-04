from unittest.mock import MagicMock, patch, sentinel

from users.sitemap import UsersSitemap


class TestUsersSitemap:

    @patch('users.sitemap.get_active_users')
    def test_items_returns_helper_result(self, helper_mock: MagicMock):
        sitemap = UsersSitemap()

        helper_mock.return_value = sentinel.user_list

        items = sitemap.items()

        assert items == sentinel.user_list
        helper_mock.assert_called_once_with()

    @patch('users.sitemap.reverse')
    def test_location_uses_reverse(self, reverse_mock: MagicMock):
        sitemap = UsersSitemap()

        reverse_mock.return_value = sentinel.location

        user = MagicMock()
        user.username = sentinel.username

        location = sitemap.location(user)

        assert location == sentinel.location
        reverse_mock.assert_called_once_with('user',
                                             args=['sentinel.username'])
