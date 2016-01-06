from django.core.files.uploadedfile import SimpleUploadedFile

from core.forms import UploadFileForm


class TestUploadFileForm:

    def test_form_renders_file_upload_field(self):
        # Given an upload file form
        form = UploadFileForm()

        # When the form is rendered
        rendered_form = form.as_p()

        # Then the upfile field is included
        assert 'id_upfile' in rendered_form

    def test_form_save(self):
        # Given a fake uploaded file
        upfile = SimpleUploadedFile('test.txt', b'test')

        # When using the file in a new form
        form = UploadFileForm({}, {'upfile': upfile})

        # Then the form is valid
        assert form.is_valid() is True
