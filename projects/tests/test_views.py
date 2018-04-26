from datetime import date, datetime
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpResponse, QueryDict
from testarsenal import DjangoTest
from freezegun import freeze_time
from projects.views import *

class MonthViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.request.user.sessions_today.side_effect = lambda d: d.day
        self.request.user.hours_worked_today.side_effect = lambda d: d.day * 2
        self.request.user.first_month.return_value = date(1983, 6, 1)
        self.request.now = datetime(1984, 10, 3)
        self.patch1 = patch("core.views.Session.group_by_date")
        self.mock_group = self.patch1.start()
        self.mock_group.return_value = [1, 2, 3]


    def tearDown(self):
        self.patch1.stop()


    def test_month_view_uses_month_template(self):
        self.check_view_uses_template(
         month, self.request, "time-tracking-month.html", 1990, 10
        )


    def test_month_view_sends_date(self):
        self.check_view_has_context(
         month, self.request, {"month": date(1990, 10, 1)}, 1990, 10
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_days(self):
        self.check_view_has_context(
         month, self.request, {"days": [1, 2, 3]}, 1984, 10
        )
        self.mock_group.assert_called_with(self.request.user, month=date(1984, 10, 1))


    @freeze_time("1984-10-3")
    def test_month_view_sends_next_month(self):
        self.check_view_has_context(month, self.request, {"next": None}, 1984, 10)
        self.check_view_has_context(
         month, self.request, {"next": date(1984, 10, 1)}, 1984, 9
        )
        self.check_view_has_context(
         month, self.request, {"next": date(1984, 2, 1)}, 1984, 1
        )
        self.check_view_has_context(
         month, self.request, {"next": date(1984, 1, 1)}, 1983, 12
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_previous_month(self):
        self.check_view_has_context(
         month, self.request, {"previous": date(1984, 9, 1)}, 1984, 10
        )
        self.check_view_has_context(
         month, self.request, {"previous": date(1983, 12, 1)}, 1984, 1
        )
        self.check_view_has_context(
         month, self.request, {"previous": None}, 1983, 6
        )


    def test_month_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(month, request, "/", 1962, 4)


    def test_month_view_raises_404_on_month_out_of_bounds(self):
        with self.assertRaises(Http404):
            month(self.request, 1961, 6)


    def test_month_view_raises_404_on_no_sessions(self):
        self.request.user.first_month.return_value = None
        with self.assertRaises(Http404):
            month(self.request, 1984, 4)



class ProjectViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("core.views.Project.objects.get")
        self.mock_get = self.patch1.start()
        self.mock_get.return_value = "PROJECT"
        self.patch2 = patch("core.views.Session.group_by_date")
        self.mock_group = self.patch2.start()
        self.mock_group.return_value = [1, 2, 3]


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_project_view_uses_project_template(self):
        self.check_view_uses_template(
         project, self.request, "project.html", 3
        )


    def test_project_view_sends_project(self):
        self.check_view_has_context(
         project, self.request, {"project": "PROJECT"}, 3
        )
        self.mock_get.assert_called_with(id=3, user=self.request.user)


    def test_project_view_sends_days(self):
        self.check_view_has_context(
         project, self.request, {"days": [1, 2, 3]}, 3
        )
        self.mock_group.assert_called_with(self.request.user, project="PROJECT")


    def test_project_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(project, request, "/", 3)


    def test_project_view_raises_404_on_non_project(self):
        self.mock_get.side_effect = Project.DoesNotExist
        with self.assertRaises(Http404):
            project(self.request, 3)



class ProjectsViewTests(DjangoTest):

    def test_projects_view_uses_projects_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(projects, request, "projects.html")


    def test_projects_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(projects, request, "/")
