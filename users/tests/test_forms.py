from unittest.mock import patch
from testarsenal import DjangoTest
from users.forms import *

class SignupFormTests(DjangoTest):

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
