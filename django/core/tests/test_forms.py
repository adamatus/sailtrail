from django.core.files.uploadedfile import SimpleUploadedFile

from core.forms import UploadFileForm


class TestUploadFileForm:

    def test_form_renders_file_upload_field(self):
        form = UploadFileForm()
        assert 'id_upfile' in form.as_p()

    def test_form_save(self):
        upfile = SimpleUploadedFile('test.txt', b'test')
        form = UploadFileForm({}, {'upfile': upfile})
        assert form.is_valid() is True
