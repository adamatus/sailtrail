"""
Activity form class
"""
from django import forms

from api.models import Activity, Boat

ERROR_ACTIVITY_NAME_MISSING = 'Please enter a name for this activity!'
ERROR_ACTIVITY_CATEGORY_MISSING = 'Please enter a category for this activity!'


class ActivityDetailsForm(forms.models.ModelForm):
    """Form for activity details"""

    def __init__(self, user, *args, **kwargs):
        """Initialize form, filtering boat list to users boats"""
        super(ActivityDetailsForm, self).__init__(*args, **kwargs)
        self.fields['boat'].queryset = Boat.objects.filter(manager=user)

    class Meta:
        model = Activity
        fields = ('name', 'description', 'private', 'category', 'boat')
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
