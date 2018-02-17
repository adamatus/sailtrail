from unittest.mock import patch, MagicMock, sentinel

from activities.forms import ActivityDetailsForm


class TestActivityDetailsForm:

    @patch('activities.forms.get_users_boats')
    def test_init_sets_queryset(self, helper_mock: MagicMock):
        # Given a boat.objects.filter mock
        helper_mock.return_value = sentinel.boats

        # when constructing a form for a user
        form = ActivityDetailsForm(user=sentinel.user)

        # then the queryset for the boat field is set
        assert form.fields['boat'].queryset == sentinel.boats
        helper_mock.assert_called_with(sentinel.user)
