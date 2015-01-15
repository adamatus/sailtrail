from django import forms
from .models import ActivityDetail

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'
ERROR_ACTIVITY_NAME_MISSING = 'Please enter a name for this activity!'
ERROR_ACTIVITY_CATEGORY_MISSING = 'Please enter a category for this activity!'


class UploadFileForm(forms.Form):
    upfile = forms.FileField(
        widget=forms.FileInput,
        label='Activity file',
        error_messages={'required': ERROR_NO_UPLOAD_FILE_SELECTED})
    activity = forms.CharField(widget=forms.HiddenInput, required=False)


class ActivityDetailsForm(forms.models.ModelForm):

    class Meta:
        model = ActivityDetail
        fields = ('name', 'description', 'category', 'activity_id')
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
            'category': {'required': ERROR_ACTIVITY_CATEGORY_MISSING},
        }
