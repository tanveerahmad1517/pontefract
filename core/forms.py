from django import forms
from django.contrib.auth import authenticate, login
from django.core.validators import MinLengthValidator
from .models import User

class SignupForm(forms.ModelForm):
    """The form users-to-be use to create a new account.

    The username, email, and password fields of the User model are used, in
    addition to a field called confirm_password. On validation, an extra step to
    check that the two password fields match is done.

    Some fields of the User model have maximum lengths, but these are removed
    from the HTML widgets themselves."""

    confirm_password_widget = forms.PasswordInput(attrs={
     "placeholder": "Confirm Password"
    })
    confirm_password = forms.CharField(widget=confirm_password_widget)

    class Meta:
        model = User
        fields = ["username", "timezone", "email", "password"]

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
        self.fields["password"].validators.append(
         MinLengthValidator(8, message="Password must be at least 8 characters")
        )
        for name in ("username", "email", "password"):
            del self.fields[name].widget.attrs["maxlength"]


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
         email=self.cleaned_data.get("email"),
         timezone=self.cleaned_data.get("timezone"),
        )
        user.set_password(self.cleaned_data.get("password"))
        user.save()
        return user



class LoginForm(forms.Form):
    """The form users use to validate who they are."""

    username_widget = forms.TextInput(attrs={
     "placeholder": "Username", "autocomplete": "off"
    })
    password_widget = forms.PasswordInput(attrs={"placeholder": "Password"})

    username = forms.CharField(widget=username_widget)
    password = forms.CharField(widget=password_widget)


    def validate_credentials(self, user_to_match=None):
        """Validates the form using full_clean, and if it's valid, tries to
        authenticate the credentials. If that succeeds, ``True`` is returned.

        If the form is invalid, or the credentials incorrect, ``False`` is
        returned.

        You can also supply a user if you want to also check that the
        credentials are for a given user."""

        if self.is_valid():
            user = authenticate(
             username=self.cleaned_data.get("username"),
             password=self.cleaned_data.get("password")
            )
            if user and (not user_to_match or user_to_match == user):
                return user
            else:
                self.add_error("username", "Invalid credentials")
        return False
