from django import forms
from .models import Activity, ActivityDetail

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'
ERROR_ACTIVITY_NAME_MISSING = 'ERROR MISSING NAME'


class UploadFileForm(forms.models.ModelForm):

    class Meta:
        model = Activity
        fields = ('upfile',)
        error_messages = {
            'upfile': {'required': ERROR_NO_UPLOAD_FILE_SELECTED},
        }


class NewActivityForm(forms.models.ModelForm):

    class Meta:
        model = ActivityDetail
        fields = ('name', 'description', 'file_id')
        error_messages = {
            'name': {'required': ERROR_ACTIVITY_NAME_MISSING},
        }

