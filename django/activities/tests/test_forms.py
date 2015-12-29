import pytest

from activities.forms import ActivityDetailsForm
from api.tests.factories import ActivityFactory


@pytest.mark.django_db
@pytest.mark.integration
class TestActivityDetailsFormIntegration:

    def test_form_renders_correct_fields(self):
        form = ActivityDetailsForm()
        assert 'id_name' in form.as_p()

    def test_form_save(self):
        a = ActivityFactory.create()
        form = ActivityDetailsForm({'name': 'Test',
                                    'description': '',
                                    'category': 'IB'},
                                   instance=a)
        form.is_valid()
        upactivity = form.save()
        assert upactivity is not None
        assert upactivity.name == 'Test'
