from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.http import QueryDict
from users.views import *

class SignupViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("users.views.SignupForm")
        self.patch2 = patch("django.contrib.auth.login")
        self.patch3 = patch("users.views.User.objects.create")
        self.mock_form = self.patch1.start()
        self.mock_login = self.patch2.start()
        self.mock_user = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_signup_view_redirects_to_home_on_get(self):
        request = self.make_request("---")
        self.check_view_redirects(signup, request, "/")


    def test_signup_view_redirects_to_home_on_successful_post(self):
        request = self.make_request("---", method="post")
        self.check_view_redirects(signup, request, "/")


    def test_signup_can_create_user(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = True
        form.data = {"username": "u", "email": "e", "password": "p"}
        user = Mock()
        self.mock_user.return_value = user
        request = self.make_request(
         "---", method="post", data={"username": "u", "email": "e"}
        )
        signup(request)
        self.mock_form.assert_called_with(QueryDict("username=u&email=e"))
        form.is_valid.assert_called_with()
        self.mock_user.assert_called_with(username="u", email="e")
        user.set_password.assert_called_with("p")
        self.mock_login.assert_called_with(request, user)


    def test_can_return_form_if_errors(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = False
        request = self.make_request(
         "---", method="post", data={"username": "u", "email": "e"}
        )
        response = signup(request)
        self.mock_form.assert_called_with(QueryDict("username=u&email=e"))
        form.is_valid.assert_called_with()
        self.assertIs(form, response)
