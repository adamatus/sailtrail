from django import forms
from .models import Activity, ActivityDetail

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'
ERROR_ACTIVITY_NAME_MISSING = 'Please enter a name for this activity!'


class UploadFileForm(forms.models.ModelForm):

    class Meta:
        model = Activity
        fields = ('upfile',)
        error_messages = {
            'upfile': {'required': ERROR_NO_UPLOAD_FILE_SELECTED},
        }


class ActivityDetailsForm(forms.models.ModelForm):

    class Meta:
        model = ActivityDetail
        fields = ('name', 'description', 'file_id')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter activity name',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Activity description',
                'class': 'form-control',
                'rows': 4,
            }),
        }
        error_messages = {
            'name': {'required': ERROR_ACTIVITY_NAME_MISSING},
        }

