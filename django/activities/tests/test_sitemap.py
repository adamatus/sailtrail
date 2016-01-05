import unittest
from unittest.mock import patch, MagicMock, sentinel

from activities.sitemap import ActivitySitemap


class TestSitemap(unittest.TestCase):

    def setUp(self):
        self.sitemap = ActivitySitemap()

    @patch('activities.sitemap.get_public_activities')
    def test_items_returns_result_of_helper(self, helper_mock: MagicMock):
        helper_mock.return_value = sentinel.activities

        items = self.sitemap.items()

        helper_mock.assert_called_with()
        assert items == sentinel.activities

    def test_lastmod_returns_activity_modified_date(self):
        activity = MagicMock()
        activity.modified = sentinel.date

        lastmod = self.sitemap.lastmod(activity)

        assert lastmod == sentinel.date
