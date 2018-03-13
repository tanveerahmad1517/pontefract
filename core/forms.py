from django import forms
from django.contrib.auth import authenticate
from .models import User

class SignupForm(forms.ModelForm):
    """The form users-to-be use to create a new account.

    The username, email, and password fields of the User model are used, in
    addition to a field called confirm_password. On validation, an extra step to
    check that the two password fields match is done.

    Some fields of the User model have maximum lengths, but these are removed
    from the HTML widgets themselves."""

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
     "placeholder": "Confirm Password"
    }))

    class Meta:
        model = User
        fields = ["username", "email", "password"]

        widgets = {
         "username": forms.TextInput(attrs={
          "autocomplete": "off", "placeholder": "Your unique username"
         }),
         "email": forms.EmailInput(attrs={
          "autocomplete": "off", "placeholder": "richard@pomfret.org"
         }),
         "password": forms.PasswordInput(attrs={
          "placeholder": "Password"
         })
        }


    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        for field in self.fields:
            try:
                del self.fields[field].widget.attrs["maxlength"]
            except KeyError: pass


    def clean(self):
        """Do the usual cleaning that a ModelForm would perform, and then also
        check that the two passwords supplied match."""

        forms.ModelForm.clean(self)
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error("password", "Passwords don't match")


    def save(self):
        """Don't rely on the built-in Model form save functionality here. Hash
        the password and login."""

        user = User.objects.create(
         username=self.cleaned_data.get("username"),
         email=self.cleaned_data.get("email")
        )
        user.set_password(self.cleaned_data.get("password"))
        user.save()
        return user



class LoginForm(forms.Form):
    """The form users use to log into their account.

    In addition to the usual Form validation, the form will also check that a
    user with the supplied actually exists."""

    username = forms.CharField(widget=forms.TextInput(attrs={
     "placeholder": "Username", "autocomplete": "off"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
     "placeholder": "Password"
    }))


    def clean(self):
        """Does this user exist?"""

        forms.Form.clean(self)
        user = authenticate(
         username=self.cleaned_data.get("username"),
         password=self.cleaned_data.get("password")
        )
        if not user: self.add_error("username", "Invalid credentials")