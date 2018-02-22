from unittest.mock import patch
from testarsenal import DjangoTest
from users.forms import *

class SignupFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("users.forms.User.objects.filter")
        self.patch2 = patch("django.forms.ModelForm.clean")
        self.mock_filter = self.patch1.start()
        self.mock_clean = self.patch2.start()
        self.mock_filter.return_value = []
        self.mock_clean.side_effect = lambda x: x.data


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_signup_form_has_correct_fields(self):
        form = SignupForm()
        self.assertEqual(
         list(form.fields.keys()),
         ["username", "email", "password", "confirm_password"]
        )


    def test_username_widget_is_correct(self):
        form = SignupForm()
        username = form.fields["username"].widget
        self.assertEqual(username.__class__.input_type, "text")
        self.assertEqual(
         username.attrs, {
          "autocomplete": "off",
          "placeholder": "Your unique username..."
         }
        )
        self.assertTrue(username.is_required)


    def test_email_widget_is_correct(self):
        form = SignupForm()
        email = form.fields["email"].widget
        self.assertEqual(email.__class__.input_type, "email")
        self.assertEqual(
         email.attrs, {
          "autocomplete": "off",
          "placeholder": "richard@pomfret.org"
         }
        )
        self.assertTrue(email.is_required)


    def test_password1_field_is_correct(self):
        form = SignupForm()
        password = form.fields["password"].widget
        self.assertEqual(password.__class__.input_type, "password")
        self.assertEqual(
         password.attrs, {
          "placeholder": "Enter a password"
         }
        )
        self.assertTrue(password.is_required)


    def test_password2_field_is_correct(self):
        form = SignupForm()
        password = form.fields["confirm_password"].widget
        self.assertEqual(password.__class__.input_type, "password")
        self.assertEqual(
         password.attrs, {
          "placeholder": "Confirm password"
         }
        )
        self.assertTrue(password.is_required)


    def test_can_validate_signup_form(self):
        form = SignupForm(data={
         "username": "u", "email": "e@b.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertTrue(form.is_valid())


    def test_form_rejects_duplicate_email(self):
        self.mock_filter.return_value = ["user"]
        form = SignupForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


    def test_form_rejects_mismatched_passwords(self):
        form = SignupForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p2"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)



class LoginFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("users.forms.authenticate")
        self.patch2 = patch("django.forms.ModelForm.clean")
        self.mock_auth = self.patch1.start()
        self.mock_clean = self.patch2.start()
        self.mock_clean.side_effect = lambda x: x.data


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_login_form_has_correct_fields(self):
        form = LoginForm()
        self.assertEqual(list(form.fields.keys()), ["username", "password"])


    def test_username_widget_is_correct(self):
        form = LoginForm()
        username = form.fields["username"].widget
        self.assertEqual(username.__class__.input_type, "text")
        self.assertEqual(
         username.attrs, {"autocomplete": "off", "placeholder": "Username"}
        )
        self.assertTrue(username.is_required)


    def test_password_field_is_correct(self):
        form = LoginForm()
        password = form.fields["password"].widget
        self.assertEqual(password.__class__.input_type, "password")
        self.assertEqual(password.attrs, {"placeholder": "Password"})
        self.assertTrue(password.is_required)


    def test_can_validate_login_form(self):
        self.mock_auth.return_value = "USER"
        form = LoginForm(data={"username": "u", "password": "p"})
        self.assertTrue(form.is_valid())
        self.mock_auth.assert_called_with(username="u", password="p")


    def test_can_reject_login_form(self):
        self.mock_auth.return_value = None
        form = LoginForm(data={"username": "u", "password": "p"})
        self.assertFalse(form.is_valid())
        self.mock_auth.assert_called_with(username="u", password="p")
