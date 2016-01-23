from unittest.mock import patch, MagicMock, sentinel, Mock

from activities.sitemap import ActivitySitemap
from api.models import Activity


class TestSitemap:

    @patch('activities.sitemap.get_public_activities')
    def test_items_returns_result_of_helper(self, helper_mock: MagicMock):
        # Given a get_activities mock that returns a sentinel
        helper_mock.return_value = sentinel.activities

        sitemap = ActivitySitemap()

        # When getting the sitemap items
        items = sitemap.items()

        # Then the sentinel will be returned
        assert items == sentinel.activities

    def test_lastmod_returns_activity_modified_date(self):
        # Given a mock activity with a sentinel date
        activity = Mock(spec=Activity, modified=sentinel.date)

        sitemap = ActivitySitemap()

        # When getting the last modified date for the item
        lastmod = sitemap.lastmod(activity)

        # Then the sentinel is returned
        assert lastmod == sentinel.date
