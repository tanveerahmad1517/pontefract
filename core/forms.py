from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ["username", "email", "password"]

        widgets = {
         "username": forms.TextInput(attrs={
          "placeholder": "Username", "autocomplete": "off"
         }),
         "email": forms.TextInput(attrs={
          "placeholder": "Email", "autocomplete": "off"
         }),
         "password": forms.PasswordInput(attrs={
          "placeholder": "Password", "autocomplete": "off"
         })
        }
