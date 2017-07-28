from unittest.mock import Mock, patch
from pontefract.tests import ViewTest
from django.http import HttpRequest, HttpResponse

class HomePageViewTests(ViewTest):

    def test_home_view_uses_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")


    @patch("timetrack.views.signup_page")
    def test_home_view_sends_signup_template_if_not_logged_in(self, mock_view):
        mock_response = HttpResponse()
        mock_view.return_value = mock_response
        self.client.logout()
        response = self.client.get("/")
        self.assertIs(response, mock_response)
