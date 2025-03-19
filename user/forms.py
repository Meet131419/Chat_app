
from django.forms import ModelForm
from django import forms
from .models import *

class ChatmessageCreateForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body', 'file']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Add message...',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm',
                'maxlength': '300',
                'autofocus': True,
            }),
            'file': forms.FileInput(attrs={
                'class': 'hidden',  # Hide the default file input
                'id': 'file-input',
                'accept': 'image/*,application/pdf,video/*,audio/*',
            }),
        }