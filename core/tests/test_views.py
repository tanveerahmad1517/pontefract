from datetime import date, datetime
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpResponse, QueryDict, Http404
from testarsenal import DjangoTest
from core.views import *

class RootViewTests(DjangoTest):

    @patch("core.views.landing")
    def test_root_view_uses_signup_view_if_logged_out(self, mock_signup):
        mock_signup.return_value = "RESPONSE"
        request = self.make_request("---")
        self.assertEqual(root(request), "RESPONSE")
        mock_signup.assert_called_with(request)


    @patch("core.views.day")
    def test_root_view_uses_home_view_if_logged_in(self, mock_day):
        mock_day.return_value = "RESPONSE"
        request = self.make_request("---", loggedin=True)
        self.assertEqual(root(request), "RESPONSE")
        mock_day.assert_called_with(request, home=True)



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



class DayViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.SessionForm")
        self.mock_form = self.patch1.start()
        self.mock_form.return_value = "FORM"
        self.patch2 = patch("core.views.process_session_form_data")
        self.mock_process = self.patch2.start()
        self.patch3 = patch("core.views.Session.from_day")
        self.mock_from = self.patch3.start()
        self.mock_from.return_value = "DAY"
        self.get = self.make_request("---", loggedin=True)
        self.post = self.make_request(
         "---", method="post", data={"u": "u", "p": "p"}, loggedin=True
        )
        self.get.now, self.post.now = datetime(2018, 1, 1), datetime(2018, 1, 1)


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_day_view_sends_day_template(self):
        self.check_view_uses_template(day, self.get, "day.html")


    def test_day_view_is_protected(self):
        request = self.make_request("---")
        self.check_view_redirects(day, request, "/")


    def test_day_view_sends_day(self):
        self.check_view_has_context(day, self.get, {"day": "DAY"})
        self.mock_from.assert_called_with(self.get.user, date(2018, 1, 1))
        self.check_view_has_context(day, self.get, {"day": "DAY"}, day="1990-09-01")
        self.mock_from.assert_called_with(self.get.user, date(1990, 9, 1))


    def test_404_on_invalid_date(self):
        with self.assertRaises(Http404):
            day(self.get, day="-098")


    def test_day_view_sends_form(self):
        self.check_view_has_context(day, self.get, {"form": "FORM"})
        self.mock_form.assert_called_with(date=date(2018, 1, 1))
        self.check_view_has_context(day, self.get, {"form": "FORM"}, day="1990-09-01")
        self.mock_form.assert_called_with(date=date(1990, 9, 1))


    def test_day_view_sends_home_flag(self):
        self.check_view_has_context(day, self.get, {"home": False})
        self.check_view_has_context(day, self.get, {"home": True}, home=True)


    def test_day_view_can_process_session_form(self):
        self.mock_process.return_value.is_valid.return_value = True
        self.check_view_redirects(day, self.post, "/day/2018-01-01/")
        self.check_view_redirects(day, self.post, "/", home=True)
        self.mock_process.assert_called_with(self.post, date=date(2018, 1, 1))
        self.mock_process.return_value.save.assert_called_with(self.post.user)


    def test_day_view_can_reject_session_form(self):
        self.mock_process.return_value.is_valid.return_value = False
        self.check_view_uses_template(day, self.post, "day.html")
        self.mock_process.assert_called_with(self.post, date=date(2018, 1, 1))
        self.assertFalse(self.mock_process.return_value.save.called)



class PolicyViewTests(DjangoTest):

    def test_policy_view_uses_policy_template(self):
        request = self.make_request("---")
        self.check_view_uses_template(policy, request, "policy.html")



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
        self.patch1 = patch("core.views.TimeSettingsForm")
        self.mock_time = self.patch1.start()
        self.patch2 = patch("core.views.AccountSettingsForm")
        self.mock_account = self.patch2.start()
        self.patch3 = patch("core.views.update_session_auth_hash")
        self.mock_update = self.patch3.start()
        self.get = self.make_request("---", loggedin=True)
        self.post = self.make_request(
         "---", method="post", data={"u": "u", "p": "p"}, loggedin=True
        )


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_profile_view_sends_profile_template(self):
        self.check_view_uses_template(profile, self.get, "profile.html")


    def test_profile_view_is_protected(self):
        request = self.make_request("---")
        self.check_view_redirects(profile, request, "/")


    def test_profile_view_sends_page_flag(self):
        self.check_view_has_context(profile, self.get, {"page": "profile"})
        self.check_view_has_context(profile, self.get, {"page": "time"}, page="time")
        self.check_view_has_context(profile, self.get, {"page": "account"}, page="account")


    def test_profile_view_sends_form(self):
        self.check_view_has_context(profile, self.get, {
         "form": self.mock_time.return_value
        }, page="time")
        self.mock_time.assert_called_with(instance=self.get.user)
        self.check_view_has_context(profile, self.get, {
         "form": self.mock_account.return_value
        }, page="account")
        self.mock_account.assert_called_with(instance=self.get.user)


    def test_profile_view_can_handle_time_saving(self):
        self.mock_time.return_value.is_valid.return_value = True
        self.check_view_redirects(profile, self.post, "/profile/time/", page="time")
        self.mock_time.assert_called_with(QueryDict("u=u&p=p"), instance=self.post.user)
        self.mock_time.return_value.save.assert_called_with()
        self.assertFalse(self.mock_update.called)


    def test_profile_view_can_handle_account_saving(self):
        self.mock_account.return_value.is_valid.return_value = True
        self.check_view_redirects(profile, self.post, "/profile/account/", page="account")
        self.mock_account.assert_called_with(QueryDict("u=u&p=p"), instance=self.post.user)
        self.mock_account.return_value.save.assert_called_with()
        self.mock_update.assert_called_with(self.post, self.mock_account.return_value.instance)


    def test_profile_view_can_reject_time_data(self):
        self.mock_time.return_value.is_valid.return_value = False
        self.check_view_uses_template(profile, self.post, "profile.html", page="time")
        self.assertFalse(self.mock_time.return_value.save.called)


    def test_profile_view_can_reject_account_data(self):
        self.mock_account.return_value.is_valid.return_value = False
        self.check_view_uses_template(profile, self.post, "profile.html", page="account")
        self.assertFalse(self.mock_account.return_value.save.called)



class AccountDeletionViewTests(DjangoTest):

    def test_account_deletion_view_uses_delete_account_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(delete_account, request, "delete-account.html")


    def test_account_deletion_view_is_protected(self):
        request = self.make_request("---")
        self.check_view_redirects(delete_account, request, "/")


    def test_account_deletion_view_can_delete_user(self):
        request = self.make_request(
         "---", loggedin=True, method="post", data={"password": "ppp"}
        )
        request.user.check_password.return_value = True
        self.check_view_redirects(delete_account, request, "/")
        request.user.check_password.assert_called_with("ppp")
        request.user.delete.assert_called_with()


    def test_account_deletion_view_can_reject_credentials(self):
        request = self.make_request(
         "---", loggedin=True, method="post", data={"password": "ppp"}
        )
        request.user.check_password.return_value = False
        self.check_view_has_context(delete_account, request, {"error": "Invalid credentials"})
        request.user.check_password.assert_called_with("ppp")
        self.assertFalse(request.user.delete.called)
