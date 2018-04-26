from datetime import date, datetime
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpResponse, QueryDict
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
        self.patch2 = patch("django.contrib.auth.login")
        self.mock_form = self.patch1.start()
        self.mock_login = self.patch2.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_landing_view_uses_landing_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(landing, request, "landing.html")


    def test_landing_view_sends_signup_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(landing, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_landing_view_processes_signup_view_on_post(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = True
        form.save.return_value = "USER"
        request = self.make_request(
         "---", method="post", data={"username": "u", "email": "e"}
        )
        self.check_view_redirects(landing, request, "/")
        self.mock_form.assert_called_with(QueryDict("username=u&email=e"))
        form.is_valid.assert_called_with()
        form.save.assert_called_with()
        self.mock_login.assert_called_with(request, "USER")


    def test_landing_view_can_send_incorrect_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = False
        request = self.make_request(
         "---", method="post", data={"username": "u", "email": "e"}
        )
        self.check_view_uses_template(landing, request, "landing.html")
        self.check_view_has_context(landing, request, {"form": form})
        self.mock_form.assert_called_with(QueryDict("username=u&email=e"))
        form.is_valid.assert_called_with()
        self.assertFalse(form.save.called)



class HomeViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.ProjectForm")
        self.mock_project_form = self.patch1.start()
        self.patch2 = patch("core.views.SessionForm")
        self.mock_form = self.patch2.start()
        self.patch4 = patch("core.views.Session.from_day")
        self.mock_from = self.patch4.start()
        self.mock_from.return_value = [date(1945, 1, 1), "B", "C"]
        self.request = self.make_request("---", loggedin=True)
        self.request.now = datetime.now()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch4.stop()


    def test_home_view_uses_home_template(self):
        self.check_view_uses_template(home, self.request, "home.html")


    def test_home_view_sends_session_form(self):
        self.mock_form.return_value = "FORM"
        self.request.user.minutes_worked_today.return_value = 19
        self.check_view_has_context(home, self.request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_home_view_sends_sessions_from_today(self):
        self.check_view_has_context(
         home, self.request, {"day": [date(1945, 1, 1), "B", "C"]}
        )
        self.mock_from.assert_called_with(self.request.user, date.today())


    def test_home_view_sends_yesterday(self):
        self.check_view_has_context(
         home, self.request, {"yesterday": date(1944, 12, 31)}
        )
        self.mock_from.assert_called_with(self.request.user, date.today())


    def test_home_view_can_return_incorrect_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = False
        form.data = {"a": "u", "b": "p"}
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}
        )
        request.now = datetime.now()
        self.check_view_uses_template(home, request, "home.html")
        self.check_view_has_context(home, request, {"form": form})
        self.mock_form.assert_called_with(QueryDict("a=u&b=p"), user=request.user)
        form.is_valid.assert_called_with()


    def test_home_view_can_save_session(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = True
        request = self.make_request(
         "---", method="post", data={"id": "xxx", "b": "C"}, loggedin=True
        )
        request.now = datetime.now()
        home(request)
        self.mock_form.assert_called_with(QueryDict("id=xxx&b=C"), user=request.user)
        self.mock_project_form.assert_called_with(request.user, QueryDict("id=xxx&b=C"))
        form.is_valid.assert_called_with()
        form.save.assert_called_with(request.user)



class LoginViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.LoginForm")
        self.mock_form = self.patch1.start()
        self.patch2 = patch("django.contrib.auth.login")
        self.patch3 = patch("django.contrib.auth.authenticate")
        self.mock_login = self.patch2.start()
        self.mock_authenticate = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_login_view_uses_login_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(login, request, "login.html")


    def test_login_view_sends_login_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---")
        self.check_view_has_context(login, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_login_view_logs_in(self):
        form = Mock()
        self.mock_form.return_value = form
        form.validate_and_login.return_value = True
        request = self.make_request(
         "---", method="post", data={"username": "u", "password": "p"}
        )
        self.check_view_redirects(login, request, "/")
        self.mock_form.assert_called_with(QueryDict("username=u&password=p"))
        form.validate_credentials.assert_called_with()


    def test_login_view_can_return_incorrect_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.validate_credentials.return_value = False
        request = self.make_request(
         "---", method="post", data={"username": "u", "password": "p"}
        )
        self.check_view_uses_template(login, request, "login.html")
        self.check_view_has_context(login, request, {"form": form})
        self.mock_form.assert_called_with(QueryDict("username=u&password=p"))
        form.validate_credentials.assert_called_with()



class LogoutViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("django.contrib.auth.logout")
        self.mock_logout = self.patch1.start()


    def tearDown(self):
        self.patch1.stop()


    def test_logout_view_logs_out_on_post(self):
        request = self.make_request("---", method="post")
        logout(request)
        self.mock_logout.assert_called_with(request)


    def test_logout_view_does_nothing_on_get(self):
        request = self.make_request("---")
        logout(request)
        self.assertFalse(self.mock_logout.called)


    def test_logout_view_redirects_home(self):
        request = self.make_request("---", method="post")
        self.check_view_redirects(logout, request, "/")



class ProfileViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.SignupForm")
        self.mock_form = self.patch1.start()


    def tearDown(self):
        self.patch1.stop()


    def test_account_deletion_view_uses_profile_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(profile, request, "profile.html")


    def test_account_deletion_view_is_protected(self):
        request = self.make_request("---")
        self.check_view_redirects(profile, request, "/")


    def test_account_deletion_view_sends_profile_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---", loggedin=True)
        self.check_view_has_context(profile, request, {"form": "FORM"})
        self.mock_form.assert_called_with(instance=request.user)


    def test_account_deletion_view_can_update_timezone(self):
        request = self.make_request(
         "---", loggedin=True, method="post", data={"timezone": "TZ"}
        )
        self.check_view_redirects(profile, request, "/profile/")
        self.assertEqual(request.user.timezone, "TZ")
        request.user.save.assert_called_with()



class AccountDeletionViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.LoginForm")
        self.mock_form = self.patch1.start()


    def tearDown(self):
        self.patch1.stop()


    def test_account_deletion_view_uses_delete_account_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(delete_account, request, "delete-account.html")


    def test_account_deletion_view_is_protected(self):
        request = self.make_request("---")
        self.check_view_redirects(delete_account, request, "/")


    def test_account_deletion_view_sends_login_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---", loggedin=True)
        self.check_view_has_context(delete_account, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_account_deletion_view_can_delete_user(self):
        user, form = Mock(), Mock()
        self.mock_form.return_value = form
        form.validate_credentials.return_value = user
        request = self.make_request(
         "---", loggedin=True, method="post", data={"a": "b"}
        )
        self.check_view_redirects(delete_account, request, "/")
        self.mock_form.assert_called_with(QueryDict("a=b"))
        form.validate_credentials.assert_called_with(user_to_match=request.user)
        user.delete.assert_called_with()


    def test_account_deletion_view_can_reject_credentials(self):
        user, form = Mock(), Mock()
        self.mock_form.return_value = form
        form.validate_credentials.return_value = False
        request = self.make_request(
         "---", loggedin=True, method="post", data={"a": "b"}
        )
        self.check_view_uses_template(delete_account, request, "delete-account.html")
        self.mock_form.assert_called_with(QueryDict("a=b"))
        form.validate_credentials.assert_called_with(user_to_match=request.user)
        self.assertFalse(user.delete.called)
