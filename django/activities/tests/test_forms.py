import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from activities.forms import UploadFileForm, ActivityDetailsForm
from activities.models import ActivityDetail
from .factories import ActivityFactory


class TestUploadFileForm:

    def test_form_renders_file_upload_field(self):
        form = UploadFileForm()
        assert 'id_upfile' in form.as_p()

    def test_form_save(self):
        upfile = SimpleUploadedFile('test.txt', b'test')
        form = UploadFileForm({}, {'upfile': upfile})
        assert form.is_valid() is True


@pytest.mark.django_db
class TestActivityDetailsForm:

    def test_form_renders_correct_fields(self):
        form = ActivityDetailsForm()
        assert 'id_name' in form.as_p()

    def test_from_save(self):
        a = ActivityFactory.create()
        form = ActivityDetailsForm({'name': 'Test',
                                    'description': '',
                                    'category': 'IB',
                                    'activity_id': a.id})
        form.is_valid()
        upactivity = form.save()
        assert upactivity is not None
        assert upactivity == ActivityDetail.objects.first()
