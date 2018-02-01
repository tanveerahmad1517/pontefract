from unittest.mock import patch
from testarsenal import DjangoTest
from core.forms import *

class UserFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.forms.User.objects.filter")
        self.patch2 = patch("django.forms.ModelForm.clean")
        self.mock_filter = self.patch1.start()
        self.mock_clean = self.patch2.start()
        self.mock_filter.return_value = []
        self.mock_clean.side_effect = lambda x: x.data


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_can_use_form(self):
        form = UserForm(data={
         "username": "u", "email": "e@b.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertTrue(form.is_valid())


    def test_form_rejects_duplicate_email(self):
        self.mock_filter.return_value = ["user"]
        form = UserForm(data={
         "username": "u", "email": "E@X.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


    def test_form_rejects_different_password(self):
        form = UserForm(data={
         "username": "u", "email": "e@b.com",
         "password": "p", "confirm_password": "x"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
