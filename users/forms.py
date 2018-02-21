from django import forms
from django.contrib.auth.models import User

class SignupForm(forms.ModelForm):

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
     "placeholder": "Confirm password", "maxlength": "128"
    }))

    class Meta:
        model = User
        fields = ["username", "email", "password"]

        widgets = {
         "username": forms.TextInput(attrs={
          "autocomplete": "off", "placeholder": "Your unique username..."
         }),
         "email": forms.EmailInput(attrs={
          "autocomplete": "off", "placeholder": "richard@pomfret.org"
         }),
         "password": forms.PasswordInput(attrs={
          "placeholder": "Enter a password"
         })
        }


    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.is_required = True
            del self.fields[field].widget.attrs["maxlength"]
