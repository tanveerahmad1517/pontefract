from pontefract.tests import ViewTest
from django.http import HttpRequest
from django.contrib.auth.models import User

class SignupPageViewTests(ViewTest):

    def setUp(self):
        ViewTest.setUp(self)
        self.client.logout()


    def test_signup_view_uses_signup_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "signup.html")


    def test_signup_view_redirects_to_self_on_post(self):
        response = self.client.post(
         "/", data={"username": "u", "email": "e", "password": "p"}
        )
        self.assertRedirects(response, "/")


    def test_signup_view_can_signup(self):
        self.assertEqual(User.objects.all().count(), 1)
        response = self.client.post(
         "/", data={"username": "u", "email": "e", "password": "p"}
        )
        self.assertEqual(User.objects.all().count(), 2)
        new_user = User.objects.last()
        self.assertEqual(new_user.username, "u")
        self.assertEqual(new_user.email, "e")


    def test_signup_view_logs_in_after_signup(self):
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(
         "/", data={"username": "u", "email": "e", "password": "p"}
        )
        self.assertIn("_auth_user_id", self.client.session)



class LoginViewTests(ViewTest):

    def test_login_view_redirects_to_home(self):
        response = self.client.post("/login/", data={
         "username": "testsam",
         "password": "testpassword"
        })
        self.assertRedirects(response, "/")
        response = self.client.get("/login/")
        self.assertRedirects(response, "/")


    def test_login_view_can_login(self):
        self.client.logout()
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post("/login/", data={
         "username": "testsam",
         "password": "testpassword"
        })
        self.assertIn("_auth_user_id", self.client.session)



class LogoutViewTests(ViewTest):

    def test_logout_view_redirects_to_home(self):
        response = self.client.get("/logout/")
        self.assertRedirects(response, "/")


    def test_logout_view_will_logout(self):
        self.assertIn("_auth_user_id", self.client.session)
        self.client.get("/logout/")
        self.assertNotIn("_auth_user_id", self.client.session)
