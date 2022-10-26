import re
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


class ApiKeyManagerForm(forms.Form):

    # Text input for user code not choice field
    user_code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width: 150px;",
                "class": "form-control",
            }
        ),
    )

    can_create_api_key = forms.BooleanField(
        required=False,
        label="Kann Api Schlüssel erstellen",
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    can_delete_api_key = forms.BooleanField(
        label="Kann API Schlüssel löschen",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    # Add lable that says "New API Key Manager can give other users API Key Manager permissions"
    can_give_ApiKeyManager_role = forms.BooleanField(
        label="Kann anderen Benutzern API Key Manager Rechte geben",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
