import random
import string
from uuid import uuid4
from django import forms
from django.forms import ModelForm
from .models import Token

# class TokenForm(ModelForm):
class TokenForm(ModelForm):
    class Meta:
        model = Token
        fields = ['user_code', 'token', 'is_active']
        widgets = {
            'user_code': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 150px;' , 'class': 'form-control'}),
            'token': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 390px;' , 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'user_code': 'User Code',
            'token': 'Token',
            'is_active': 'Is Active',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
        }

        error_messages = {
            'user_code': {
                'required': 'User Code is required.',
            },
            'token': {
                'required': 'Token is required.',
            },
            'is_active': {
                'required': 'Is Active is required.',
            },
            'created_at': {
                'required': 'Created At is required.',
            },
            'updated_at': {
                'required': 'Updated At is required.',
            },
        }