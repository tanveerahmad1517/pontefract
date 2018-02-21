from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from core.views import *

class RootViewTests(DjangoTest):

    @patch("core.views.signup")
    def test_root_view_uses_signup_view(self, mock_signup):
        mock_signup.return_value = "RESPONSE"
        request = self.make_request("---")
        self.assertEqual(root(request), "RESPONSE")
        mock_signup.assert_called_with(request)



class SignupViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.SignupForm")
        self.mock_form = self.patch1.start()


    def tearDown(self):
        self.patch1.stop()


    def test_signup_view_uses_signup_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(signup, request, "landing.html")


    def test_signup_view_sends_signup_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(signup, request, {"form": "FORM"})
        self.mock_form.assert_called_with()
