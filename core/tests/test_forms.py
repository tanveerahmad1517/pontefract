from unittest.mock import patch, Mock
from testarsenal import DjangoTest
from core.forms import *

class SignupFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("django.forms.ModelForm.clean")
        self.patch2 = patch("core.forms.User.objects.create")
        self.mock_clean = self.patch1.start()
        self.mock_create = self.patch2.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_signup_form_has_correct_fields(self):
        form = SignupForm()
        self.assertEqual(
         list(form.fields.keys()),
         ["username", "email", "password", "confirm_password"]
        )


    def test_username(self):
        username = SignupForm().fields["username"]
        widget = username.widget
        self.assertEqual(widget.input_type, "text")
        self.assertEqual(widget.attrs, {
         "autocomplete": "off", "placeholder": "Your unique username"
        })


    def test_email(self):
        email = SignupForm().fields["email"]
        widget = email.widget
        self.assertEqual(widget.input_type, "email")
        self.assertEqual(widget.attrs, {
         "autocomplete": "off",  "placeholder": "richard@pomfret.org"
        })


    def test_password_1(self):
        password = SignupForm().fields["password"]
        widget = password.widget
        self.assertEqual(widget.input_type, "password")
        self.assertEqual(widget.attrs, {"placeholder": "Password"})


    def test_password_2(self):
        password = SignupForm().fields["confirm_password"]
        widget = password.widget
        self.assertEqual(widget.input_type, "password")
        self.assertEqual(widget.attrs, {"placeholder": "Confirm Password"})


    def test_can_validate_signup_form(self):
        form = SignupForm(data={
         "username": "u", "email": "e@b.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertTrue(form.is_valid())
        self.mock_clean.assert_called_with(form)


    def test_form_rejects_mismatched_passwords(self):
        form = SignupForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p2"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.mock_clean.assert_called_with(form)


    def test_saving_saves_user_properly(self):
        user = Mock()
        self.mock_create.return_value = user
        form = SignupForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p"
        })
        form.is_valid()
        returned = form.save()
        self.mock_create.assert_called_with(username="u", email="E@X.com")
        user.set_password.assert_called_with("p")
        user.save.assert_called_with()
        self.assertIs(returned, user)



class LoginFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.forms.authenticate")
        self.patch2 = patch("django.forms.Form.clean")
        self.mock_auth = self.patch1.start()
        self.mock_clean = self.patch2.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_login_form_has_correct_fields(self):
        form = LoginForm()
        self.assertEqual(list(form.fields.keys()), ["username", "password"])


    def test_username(self):
        username = LoginForm().fields["username"]
        widget = username.widget
        self.assertEqual(widget.input_type, "text")
        self.assertEqual(widget.attrs, {
         "autocomplete": "off", "placeholder": "Username"
        })


    def test_password(self):
        password = LoginForm().fields["password"]
        widget = password.widget
        self.assertEqual(widget.input_type, "password")
        self.assertEqual(widget.attrs, {"placeholder": "Password"})


    def test_can_validate_login_form(self):
        self.mock_auth.return_value = "USER"
        form = LoginForm(data={"username": "u", "password": "p"})
        self.assertTrue(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.mock_auth.assert_called_with(username="u", password="p")


    def test_can_reject_login_form(self):
        self.mock_auth.return_value = None
        form = LoginForm(data={"username": "u", "password": "p"})
        self.assertFalse(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.mock_auth.assert_called_with(username="u", password="p")
