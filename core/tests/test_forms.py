from unittest.mock import patch, Mock
from testarsenal import DjangoTest
from django.core.exceptions import ValidationError
from core.forms import *

class SignupFormTests(DjangoTest):

    def test_signup_form_has_correct_fields(self):
        form = SignupForm()
        self.assertEqual(
         list(form.fields.keys()),
         ["username", "email", "password", "confirm_password"]
        )


    def test_username_widget(self):
        widget = SignupForm().fields["username"].widget
        self.assertEqual(widget.input_type, "text")
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.attrs, {
         "autocomplete": "off", "placeholder": "Your unique username"
        })


    def test_email_widget(self):
        widget = SignupForm().fields["email"].widget
        self.assertEqual(widget.input_type, "email")
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.attrs, {
         "autocomplete": "off",  "placeholder": "richard@pomfret.org"
        })


    def test_username_validation(self):
        username = LoginForm().fields["username"]
        self.assertTrue(username.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                username.clean(invalid)



    def test_email_validation(self):
        email = SignupForm().fields["email"]
        self.assertTrue(email.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                email.clean(invalid)


    def test_password_1_widget(self):
        widget = SignupForm().fields["password"].widget
        self.assertEqual(widget.input_type, "password")
        self.assertEqual(widget.attrs, {"placeholder": "Password"})


    def test_password_1_validation(self):
        password = SignupForm().fields["password"]
        self.assertTrue(password.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                password.clean(invalid)


    def test_password_2(self):
        widget = SignupForm().fields["confirm_password"].widget
        self.assertEqual(widget.input_type, "password")
        self.assertEqual(widget.attrs, {"placeholder": "Confirm Password"})


    def test_password_2_validation(self):
        password = SignupForm().fields["confirm_password"]
        self.assertTrue(password.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                password.clean(invalid)


    @patch("django.forms.ModelForm.clean")
    @patch("core.forms.SignupForm.add_error")
    def test_form_accepts_matched_passwords(self, mock_add, mock_clean):
        form = SignupForm(data={"password": "p", "confirm_password": "p2"})
        form.cleaned_data = {"password": "p", "confirm_password": "p"}
        form.clean()
        mock_clean.assert_called_with(form)
        self.assertFalse(mock_add.called)


    @patch("django.forms.ModelForm.clean")
    @patch("core.forms.SignupForm.add_error")
    def test_form_rejects_mismatched_passwords(self, mock_add, mock_clean):
        form = SignupForm(data={"password": "p", "confirm_password": "p2"})
        form.cleaned_data = {"password": "p", "confirm_password": "p2"}
        form.clean()
        mock_clean.assert_called_with(form)
        mock_add.assert_called_with("password", "Passwords don't match")


    @patch("core.forms.User.objects.create")
    def test_saving_saves_user_properly(self, mock_create):
        user = Mock()
        mock_create.return_value = user
        form = SignupForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p"
        })
        form.cleaned_data = {
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p"
        }
        returned = form.save()
        mock_create.assert_called_with(username="u", email="E@X.com")
        user.set_password.assert_called_with("p")
        user.save.assert_called_with()
        self.assertIs(returned, user)



class LoginFormTests(DjangoTest):

    def test_login_form_has_correct_fields(self):
        form = LoginForm()
        self.assertEqual(list(form.fields.keys()), ["username", "password"])


    def test_username_widget(self):
        widget = LoginForm().fields["username"].widget
        self.assertEqual(widget.input_type, "text")
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.attrs, {
         "autocomplete": "off", "placeholder": "Username"
        })


    def test_password_widget(self):
        widget = LoginForm().fields["password"].widget
        self.assertEqual(widget.input_type, "password")
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.attrs, {"placeholder": "Password"})


    def test_username_validation(self):
        username = LoginForm().fields["username"]
        self.assertTrue(username.required)


    def test_password_validation(self):
        password = LoginForm().fields["password"]
        self.assertTrue(password.required)


    @patch("core.forms.LoginForm.is_valid")
    @patch("core.forms.authenticate")
    @patch("core.forms.login")
    def test_can_validate_and_login(self, mock_login, mock_auth, mock_valid):
        mock_valid.return_value = True
        request = Mock()
        mock_auth.return_value = "USER"
        form = LoginForm(data={"a": 1, "b": 2})
        form.cleaned_data = {"username": "u", "password": "p"}
        self.assertTrue(form.validate_and_login(request))
        mock_valid.assert_called_with()
        mock_auth.assert_called_with(username="u", password="p")
        mock_login.assert_called_with(request, "USER")


    @patch("core.forms.LoginForm.is_valid")
    @patch("core.forms.authenticate")
    @patch("core.forms.login")
    def test_can_reject_validation(self, mock_login, mock_auth, mock_valid):
        mock_valid.return_value = False
        request = Mock()
        form = LoginForm(data={"a": 1, "b": 2})
        self.assertFalse(form.validate_and_login(request))
        mock_valid.assert_called_with()
        self.assertFalse(mock_auth.called)
        self.assertFalse(mock_login.called)


    @patch("core.forms.LoginForm.is_valid")
    @patch("core.forms.authenticate")
    @patch("core.forms.login")
    @patch("core.forms.LoginForm.add_error")
    def test_can_reject_credentials(self, mock_add, mock_login, mock_auth, mock_valid):
        mock_valid.return_value = True
        request = Mock()
        mock_auth.return_value = None
        form = LoginForm(data={"a": 1, "b": 2})
        form.cleaned_data = {"username": "u", "password": "p"}
        self.assertFalse(form.validate_and_login(request))
        mock_valid.assert_called_with()
        mock_auth.assert_called_with(username="u", password="p")
        self.assertFalse(mock_login.called)
        mock_add.assert_called_with("username", "Invalid credentials")
