from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from multiupload.fields import MultiFileField

from .models import Activity

User = get_user_model()

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'
ERROR_ACTIVITY_NAME_MISSING = 'Please enter a name for this activity!'
ERROR_ACTIVITY_CATEGORY_MISSING = 'Please enter a category for this activity!'
ERROR_UNSUPPORTED_FILE_TYPE = 'Only GPX and SBN files are currently supported.'


class UploadFileForm(forms.Form):
    upfile = MultiFileField(
        min_num=1,
        max_num=24,
        max_file_size=1014*1024*24,
        label='Activity file',
        error_messages={'required': ERROR_NO_UPLOAD_FILE_SELECTED}
    )


class ActivityDetailsForm(forms.models.ModelForm):

    class Meta:
        model = Activity
        fields = ('name', 'description', 'private', 'category')
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
            'private': forms.CheckboxInput(attrs={
                'label': 'Private'
            }),
        }
        error_messages = {
            'name': {'required': ERROR_ACTIVITY_NAME_MISSING},
            'category': {'required': ERROR_ACTIVITY_CATEGORY_MISSING},
        }


class NewUserForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "email")
