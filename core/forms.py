from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):


    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
     "placeholder": "Confirm Password", "autocomplete": "off"
    }))

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


    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('password', "Passwords don't match")
