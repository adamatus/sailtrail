from django import forms
from .models import Activity

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'


class UploadFileForm(forms.models.ModelForm):

    class Meta:
        model = Activity
        fields = ('upfile',)
        error_messages = {
            'upfile': {'required': ERROR_NO_UPLOAD_FILE_SELECTED},
        }
