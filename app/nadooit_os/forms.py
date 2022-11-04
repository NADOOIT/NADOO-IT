from cProfile import label
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
        label="Schlüssel User code eingeben:",
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
        label="Schlüssel User code eingeben:",
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
    can_give_manager_role = forms.BooleanField(
        label="Kann Schlüßel API Key Manager Rechte vergeben",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class CustomerTimeAccountManagerForm(forms.Form):

    # Text input for user code not choice field
    user_code = forms.CharField(
        required=True,
        label="Schlüssel User code eingeben:",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "style": "width: 150px;",
                "class": "form-control",
            }
        ),
    )

    can_create_time_accounts = forms.BooleanField(
        required=False,
        label="Kann Zeitkonten erstellen",
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    can_delete_time_accounts = forms.BooleanField(
        label="Kann Zeitkonten löschen",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    # Add lable that says "New API Key Manager can give other users API Key Manager permissions"
    can_give_Customer_Time_Account_Manager_role = forms.BooleanField(
        label="Kann Schlüßel Zeitkonto Manager Rechte vergeben",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
