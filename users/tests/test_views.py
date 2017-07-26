from pontefract.tests import ViewTest
from django.http import HttpRequest

class SignupPageViewTests(ViewTest):

    def test_signup_view_uses_signup_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "signup.html")
