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

    def test_signup_view_uses_signup_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(signup, request, "signup.html")
