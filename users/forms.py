from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

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


    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        if User.objects.filter(email=cleaned_data["email"]):
            self.add_error("email", "That email address is already in use")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error("password", "Passwords don't match")



class LoginForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={
     "placeholder": "Username", "autocomplete": "off"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
     "placeholder": "Password"
    }))

    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        user = authenticate(
         username=cleaned_data.get("username"),
         password=cleaned_data.get("password")
        )
        if not user:
            self.add_error("username", "Invalid credentials")
