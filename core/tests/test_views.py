from datetime import date
from unittest.mock import patch, Mock, MagicMock
from freezegun import freeze_time
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
        self.patch3 = patch("core.views.Project.by_name")
        self.mock_by = self.patch3.start()
        self.mock_by.return_value = [1, 2, 3]


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_home_view_uses_home_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(home, request, "home.html")


    def test_home_view_sends_session_form(self):
        self.mock_form.return_value = "FORM"
        request = self.make_request("---", loggedin=True)
        request.user.minutes_worked_today.return_value = 19
        self.check_view_has_context(home, request, {"form": "FORM"})
        self.mock_form.assert_called_with()


    def test_home_view_sends_session_user_projects(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_has_context(home, request, {"project_list": ["1", "2", "3"]})


    def test_home_view_can_return_incorrect_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.is_valid.return_value = False
        form.data = {"a": "u", "b": "p"}
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}
        )
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


    def test_login_view_logs_inn(self):
        form = Mock()
        self.mock_form.return_value = form
        form.validate_and_login.return_value = True
        request = self.make_request(
         "---", method="post", data={"username": "u", "password": "p"}
        )
        self.check_view_redirects(login, request, "/")
        self.mock_form.assert_called_with(QueryDict("username=u&password=p"))
        form.validate_and_login.assert_called_with(request)


    def test_login_view_can_return_incorrect_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.validate_and_login.return_value = False
        request = self.make_request(
         "---", method="post", data={"username": "u", "password": "p"}
        )
        self.check_view_uses_template(login, request, "login.html")
        self.check_view_has_context(login, request, {"form": form})
        self.mock_form.assert_called_with(QueryDict("username=u&password=p"))
        form.validate_and_login.assert_called_with(request)



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



class TimeTrackingMonthViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.request.user.sessions_today.side_effect = lambda d: d.day
        self.request.user.hours_worked_today.side_effect = lambda d: d.day * 2
        self.request.user.first_month.return_value = date(1983, 6, 1)


    def test_month_view_uses_month_template(self):
        self.check_view_uses_template(
         time_month, self.request, "time-month.html", 1990, 10
        )


    def test_month_view_sends_date(self):
        self.check_view_has_context(
         time_month, self.request, {"month": date(1990, 10, 1)}, 1990, 10
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_days(self):
        self.check_view_has_context(time_month, self.request, {"days": [
         (date(1984, 10, 3), 6, 3), (date(1984, 10, 2), 4, 2), (date(1984, 10, 1), 2, 1)
        ]}, 1984, 10)
        self.check_view_has_context(time_month, self.request, {"days": [
         (date(1984, 9, n), n * 2, n) for n in range(1, 31)
        ][::-1]}, 1984, 9)


    @freeze_time("1984-10-3")
    def test_month_view_sends_next_month(self):
        self.check_view_has_context(time_month, self.request, {"next": None}, 1984, 10)
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 10, 1)}, 1984, 9
        )
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 2, 1)}, 1984, 1
        )
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 1, 1)}, 1983, 12
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_previous_month(self):
        self.check_view_has_context(
         time_month, self.request, {"previous": date(1984, 9, 1)}, 1984, 10
        )
        self.check_view_has_context(
         time_month, self.request, {"previous": date(1983, 12, 1)}, 1984, 1
        )
        self.check_view_has_context(
         time_month, self.request, {"previous": None}, 1983, 6
        )


    def test_month_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(time_month, request, "/", 1962, 4)


    def test_month_view_raises_404_on_month_out_of_bounds(self):
        with self.assertRaises(Http404):
            time_month(self.request, 1961, 6)
