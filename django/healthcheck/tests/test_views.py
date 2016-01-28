from unittest.mock import patch, Mock, sentinel

from healthcheck.views import check_db, HealthcheckView


class TestCheckDb:

    @patch('healthcheck.views.Healthcheck')
    def test_check_db_creates_object(self, mock):
        # When checking DB
        check_db()

        # Then mock is called
        mock.objects.create.assert_called_once_with(source="DB")


class TestHealthCheckView:

    @patch('healthcheck.views.HttpResponseServerError')
    @patch('healthcheck.views.check_db')
    def test_returns_500_if_db_check_throws(self, check_db_mock, resp_mock):
        check_db_mock.side_effect = Exception

        resp_mock.return_value = sentinel.response

        view = HealthcheckView()
        response = view.get(Mock())

        assert response == sentinel.response

    @patch('healthcheck.views.HttpResponse')
    @patch('healthcheck.views.check_db')
    def test_returns_200_if_db_check_ok(self, check_db_mock, resp_mock):
        resp_mock.return_value = sentinel.response

        view = HealthcheckView()
        response = view.get(Mock())

        assert response == sentinel.response
