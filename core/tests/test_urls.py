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


    def test_time_tracking_month_url(self):
        self.check_url_returns_view("/time/1990/09/", project_views.month)


    def test_time_tracking_project_url(self):
        self.check_url_returns_view("/projects/199/", project_views.project)


    def test_time_tracking_projects_url(self):
        self.check_url_returns_view("/projects/", project_views.projects)


    def test_time_tracking_edit_session_url(self):
        self.check_url_returns_view("/sessions/199/", project_views.edit_session)
