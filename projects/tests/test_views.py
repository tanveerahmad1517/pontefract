from datetime import date, datetime
from unittest.mock import patch, Mock, MagicMock
from django.http import HttpResponse, QueryDict
from testarsenal import DjangoTest
from freezegun import freeze_time
from projects.views import *

class TimeViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("projects.views.Session.from_month")
        self.mock_month = self.patch1.start()
        self.patch2 = patch("projects.views.Session.from_project")
        self.mock_project = self.patch2.start()
        self.patch3 = patch("projects.views.get_object_or_404")
        self.mock_get = self.patch3.start()
        self.request = self.make_request("---", loggedin=True)


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_times_view_uses_time_template(self):
        self.check_view_uses_template(time, self.request, "time.html")


    def test_projects_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(time, request, "/")


    def test_time_view_can_send_month_sessions(self):
        self.check_view_has_context(time, self.request, {
         "title": "September 1990",
         "days": self.mock_month.return_value,
         "month_date": date(1990, 9, 1),
         "project": None
        }, month="1990-09")
        self.mock_month.assert_called_with(self.request.user, date(1990, 9, 1))


    def test_time_view_can_send_project_sessions(self):
        self.check_view_has_context(time, self.request, {
         "title": self.mock_get.return_value.name,
         "days": self.mock_project.return_value,
         "month_date": None,
         "project": self.mock_get.return_value
        }, project="123")
        self.mock_get.assert_called_with(Project, id="123", user=self.request.user)
        self.mock_project.assert_called_with(self.mock_get.return_value)



class ProjectsViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.Project.by_user_order")
        self.mock_all = self.patch1.start()
        self.mock_all.return_value = "PROJECTS"


    def tearDown(self):
        self.patch1.stop()


    def test_projects_view_uses_project_template(self):
        self.check_view_uses_template(projects, self.request, "projects.html")


    def test_projects_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(projects, request, "/")


    def test_projects_view_sends_projects(self):
        self.check_view_has_context(
         projects, self.request, {"projects": "PROJECTS"}
        )
        self.mock_all.assert_called_with(self.request.user)



class EditSessionViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.mock_get.return_value = "SESSION"
        self.patch2 = patch("projects.views.SessionForm")
        self.mock_form = self.patch2.start()
        self.mock_form.return_value = "FORM"
        self.patch3 = patch("projects.views.process_session_form_data")
        self.mock_process = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_edit_session_view_uses_edit_session_template(self):
        self.check_view_uses_template(
         edit_session, self.request, "edit-session.html", 3
        )


    def test_edit_session_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(edit_session, request, "/", 3)


    def test_edit_session_view_sends_form(self):
        self.check_view_has_context(
         edit_session, self.request, {"form": "FORM"}, 3
        )
        self.mock_get.assert_called_with(Session, id=3, project__user=self.request.user)
        self.mock_form.assert_called_with(instance="SESSION")


    def test_edit_session_view_can_return_incorrect_form(self):
        self.mock_process.return_value = Mock()
        self.mock_process.return_value.is_valid.return_value = False
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}, loggedin=True
        )
        self.check_view_uses_template(edit_session, request, "edit-session.html", 3)
        self.mock_process.assert_called_with(request, instance="SESSION")


    def test_edit_session_view_can_save_changes(self):
        self.mock_process.return_value = Mock()
        self.mock_process.return_value.instance.local_start.return_value = datetime(1998, 1, 3, 4, 5, 6)
        self.mock_process.return_value.is_valid.return_value = True
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}, loggedin=True
        )
        self.check_view_redirects(edit_session, request, "/day/1998-01-03/", 3)
        self.mock_process.assert_called_with(request, instance="SESSION")
        self.mock_process.return_value.save.assert_called_with(request.user)



class DeleteSessionViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.session = Mock()
        self.session.local_start.return_value = datetime(1998, 1, 3, 4, 5, 6)
        self.mock_get.return_value = self.session


    def tearDown(self):
        self.patch1.stop()


    def test_delete_session_view_uses_delete_session_template(self):
        self.check_view_uses_template(
         delete_session, self.request, "delete-session.html", 3
        )


    def test_delete_session_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(delete_session, request, "/", 3)


    def test_delete_session_view_sends_session(self):
        self.check_view_has_context(
         delete_session, self.request, {"session": self.session}, 3
        )
        self.mock_get.assert_called_with(Session, id=3, project__user=self.request.user)


    def test_delete_session_can_delete_session(self):
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}, loggedin=True
        )
        self.check_view_redirects(delete_session, request, "/day/1998-01-03/", 3)
        self.session.delete.assert_called_with()



class NewProjectViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.ProjectForm")
        self.mock_form = self.patch1.start()
        self.mock_form.return_value = "FORM"


    def tearDown(self):
        self.patch1.stop()


    def test_new_project_view_uses_new_project_template(self):
        self.check_view_uses_template(
         new_project, self.request, "new-project.html"
        )


    def test_new_project_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(new_project, request, "/")


    def test_new_project_view_sends_project_form(self):
        self.mock_form.return_value = "FORM"
        self.check_view_has_context(new_project, self.request, {"form": "FORM"})
        self.mock_form.assert_called_with(user=self.request.user)


    def test_can_save_new_project(self):
        form = Mock()
        self.mock_form.return_value = form
        form.instance.id = 10
        form.is_valid.return_value = True
        request = self.make_request("---", loggedin=True, data={"a": "b"}, method="post")
        self.check_view_redirects(new_project, request, "/projects/10/")
        self.mock_form.assert_called_with(user=request.user, data=QueryDict("a=b"))
        form.save.assert_called_with()


    def test_can_reject_invalid_form(self):
        form = Mock()
        self.mock_form.return_value = form
        form.instance.id = 10
        form.is_valid.return_value = False
        request = self.make_request("---", loggedin=True, data={"a": "b"}, method="post")
        self.check_view_uses_template(new_project, request, "new-project.html")
        self.mock_form.assert_called_with(user=request.user, data=QueryDict("a=b"))
        self.assertFalse(form.save.called)



class EditProjectViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.ProjectForm")
        self.mock_form = self.patch1.start()
        self.mock_form.return_value = "FORM"
        self.patch2 = patch("projects.views.get_object_or_404")
        self.mock_get = self.patch2.start()
        self.mock_get.return_value = "PROJECT"


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_edit_project_view_uses_edit_project_template(self):
        self.check_view_uses_template(
         edit_project, self.request, "edit-project.html", 4
        )


    def test_edit_project_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(edit_project, request, "/", 4)


    def test_edit_project_view_sends_form(self):
        self.check_view_has_context(edit_project, self.request, {"form": "FORM"}, 4)
        self.mock_get.assert_called_with(Project, id=4, user=self.request.user)
        self.mock_form.assert_called_with(user=self.request.user, instance="PROJECT")


    def test_can_save_edited_project(self):
        form = Mock()
        self.mock_form.return_value = form
        form.instance.id = 10
        form.is_valid.return_value = True
        request = self.make_request("---", loggedin=True, data={"a": "b"}, method="post")
        self.check_view_redirects(edit_project, request, "/projects/10/", 10)
        self.mock_get.assert_called_with(Project, id=10, user=request.user)
        self.mock_form.assert_called_with(
         user=request.user, instance="PROJECT", data=QueryDict("a=b")
        )
        form.save.assert_called_with()


    def test_can_reject_invalid_form_project(self):
        form = Mock()
        self.mock_form.return_value = form
        form.instance.id = 10
        form.is_valid.return_value = False
        request = self.make_request("---", loggedin=True, data={"a": "b"}, method="post")
        self.check_view_uses_template(edit_project, request, "edit-project.html", 10)
        self.mock_get.assert_called_with(Project, id=10, user=request.user)
        self.mock_form.assert_called_with(
         user=request.user, instance="PROJECT", data=QueryDict("a=b")
        )
        self.assertFalse(form.save.called)



class DeleteProjectViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("projects.views.get_object_or_404")
        self.mock_get = self.patch1.start()
        self.project = Mock()
        self.mock_get.return_value = self.project


    def tearDown(self):
        self.patch1.stop()


    def test_delete_project_view_uses_delete_project_template(self):
        self.check_view_uses_template(
         delete_project, self.request, "delete-project.html", 3
        )


    def test_delete_project_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(delete_project, request, "/", 3)


    def test_delete_project_view_sends_project(self):
        self.check_view_has_context(
         delete_project, self.request, {"project": self.project}, 3
        )
        self.mock_get.assert_called_with(Project, id=3, user=self.request.user)


    def test_delete_project_can_delete_project(self):
        request = self.make_request(
         "---", method="post", data={"a": "u", "b": "p"}, loggedin=True
        )
        self.check_view_redirects(delete_project, request, "/projects/", 3)
        self.project.delete.assert_called_with()
