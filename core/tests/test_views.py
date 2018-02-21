from unittest.mock import patch, Mock, MagicMock
from testarsenal import DjangoTest
from core.views import *

class RootViewTests(DjangoTest):

    @patch("core.views.landing")
    def test_root_view_uses_signup_view_if_logged_out(self, mock_signup):
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



class LandingViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.SignupForm")
        self.mock_form = self.patch1.start()


    def tearDown(self):
        self.patch1.stop()


    def test_landing_view_uses_landing_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(landing, request, "landing.html")


    def test_landing_view_sends_signup_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(landing, request, {"form": "FORM"})
        self.mock_form.assert_called_with()



class HomeViewTests(DjangoTest):

    def test_home_view_uses_home_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(home, request, "home.html")
