from django import forms
from .models import ContentPage


class UploadZipForm(forms.Form):
    file = forms.FileField()


class ContentPageForm(forms.ModelForm):
    class Meta:
        model = ContentPage
        fields = ["title", "slug", "html", "css", "js", "is_published"]
