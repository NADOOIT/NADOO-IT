import uuid
from django import forms
from nadooit_auth.models import User
from django.forms import ModelChoiceField


class UserCodeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user_code


class ApiKeyForm(forms.Form):
    user_code = UserCodeModelChoiceField(
        queryset=User.objects.all(),
        to_field_name="user_code",
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "style": "width: 150px;",
                "class": "form-control",
            }
        ),
    )
    api_key = forms.UUIDField(
        initial=uuid.uuid4,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width: 390px;",
                "class": "form-control",
            }
        ),
    )
    is_active = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
