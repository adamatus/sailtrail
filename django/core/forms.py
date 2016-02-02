"""
Activity form class
"""
from django import forms
from multiupload.fields import MultiFileField

ERROR_NO_UPLOAD_FILE_SELECTED = 'Please choose a file before clicking upload!'
ERROR_UNSUPPORTED_FILE_TYPE = 'Only GPX and SBN files are currently supported.'


class UploadFileForm(forms.Form):
    """Form for uploading files"""
    upfile = MultiFileField(
        min_num=1,
        max_num=24,
        max_file_size=1014*1024*24,
        label='Activity file',
        error_messages={'required': ERROR_NO_UPLOAD_FILE_SELECTED}
    )
