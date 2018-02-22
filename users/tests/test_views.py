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



class LoginViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("users.views.LoginForm")
        self.patch2 = patch("django.contrib.auth.login")
        self.patch3 = patch("django.contrib.auth.authenticate")
        self.mock_form = self.patch1.start()
        self.mock_login = self.patch2.start()
        self.mock_authenticate = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_login_view_uses_login_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(login, request, "login.html")


    def test_login_view_sends_signup_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(login, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_login_form_redirects_on_successful_post(self):
        request = self.make_request("---", method="post")
        self.check_view_redirects(login, request, "/")


    def test_login_form_can_login(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = True
        form.data = {"username": "u", "password": "p"}
        self.mock_authenticate.return_value = "USER"
        request = self.make_request(
         "---", method="post", data={"username": "u", "password": "p"}
        )
        login(request)
        self.mock_form.assert_called_with(QueryDict("username=u&password=p"))
        form.is_valid.assert_called_with()
        self.mock_authenticate.assert_called_with(username="u", password="p")
        self.mock_login.assert_called_with(request, "USER")
