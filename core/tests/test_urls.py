from testarsenal import DjangoTest
import core.views as core_views
import projects.views as project_views

class UrlTests(DjangoTest):

    def test_root_url(self):
        self.check_url_returns_view("/", core_views.root)


    def test_login_url(self):
        self.check_url_returns_view("/login/", core_views.login)


    def test_logout_url(self):
        self.check_url_returns_view("/logout/", core_views.logout)


    def test_profile_url(self):
        self.check_url_returns_view("/profile/", core_views.profile)


    def test_delete_account_url(self):
        self.check_url_returns_view("/delete-account/", core_views.delete_account)


    def test_day_url(self):
        self.check_url_returns_view("/time/1990/09/04/", project_views.day)


    def test_month_url(self):
        self.check_url_returns_view("/time/1990/09/", project_views.month)


    def test_project_url(self):
        self.check_url_returns_view("/projects/199/", project_views.project)


    def test_projects_url(self):
        self.check_url_returns_view("/projects/", project_views.projects)


    def test_edit_session_url(self):
        self.check_url_returns_view("/sessions/199/", project_views.edit_session)


    def test_delete_session_url(self):
        self.check_url_returns_view("/sessions/199/delete/", project_views.delete_session)


    def test_new_project_url(self):
        self.check_url_returns_view("/projects/new/", project_views.new_project)


    def test_edit_project_url(self):
        self.check_url_returns_view("/projects/199/edit/", project_views.edit_project)
