from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from django.http import Http404, QueryDict
from core.views import *

class RootViewTests(DjangoTest):

    @patch("core.views.signup")
    def test_root_view_uses_signup_view(self, mock_signup):
        mock_signup.return_value = "RESPONSE"
        request = self.make_request("---")
        self.assertEqual(root(request), "RESPONSE")
        mock_signup.assert_called_with(request)


    @patch("core.views.home")
    def test_root_view_uses_home_view_if_logged_in(self, mock_home):
        mock_home.return_value = "RESPONSE"
        request = self.make_request("---", loggedin=True)
        self.assertEqual(root(request), "RESPONSE")
        mock_home.assert_called_with(request)



class SignupViewTests(DjangoTest):

    def setUp(self):
        self.patcher1 = patch("core.views.UserForm")
        self.patcher2 = patch("core.views.login")
        self.mock_form = self.patcher1.start()
        self.mock_login = self.patcher2.start()


    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()


    def test_signup_view_uses_signup_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(signup, request, "signup.html")


    def test_signup_view_sends_fresh_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(signup, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_signup_view_redirects_home_on_post(self):
        request = self.make_request("---", method="post", data={
         "username": "u", "email": "e", "password": "p", "password2": "p"
        })
        self.check_view_redirects(signup, request, "/")


    def test_signup_view_can_create_user(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = True
        form.save.return_value = "USER"
        request = self.make_request("---", method="post", data={
         "username": "u", "email": "e"
        })
        signup(request)
        self.mock_form.assert_called_with(QueryDict("username=u&email=e"))
        form.is_valid.assert_called_with()
        form.save.assert_called_with()
        self.mock_login.assert_called_with(request, "USER")



class HomeViewTests(DjangoTest):

    def test_home_view_uses_home_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(home, request, "home.html")
