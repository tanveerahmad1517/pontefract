from testarsenal import DjangoTest
from core.forms import *

class UserFormTests(DjangoTest):

    def setUp(self):
        User.objects.create(username="A", email="E@X.com")
        

    def test_can_use_form(self):
        form = UserForm(data={
         "username": "u", "email": "e@b.com",
         "password": "p", "confirm_password": "p"
        })
        self.assertTrue(form.is_valid())


    def test_form_rejects_duplicate_email(self):
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
