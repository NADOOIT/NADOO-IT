from django import forms


class UploadZipForm(forms.Form):
    file = forms.FileField()
