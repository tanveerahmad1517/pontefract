from testarsenal import DjangoTest
import core.views as core_views

class UrlTests(DjangoTest):

    def test_root_url(self):
        self.check_url_returns_view("/", core_views.root)


    def test_login_url(self):
        self.check_url_returns_view("/login/", core_views.login)


    def test_logout_url(self):
        self.check_url_returns_view("/logout/", core_views.logout)


    def test_time_tracking_month_url(self):
        self.check_url_returns_view("/time/1990/09/", core_views.time_month)


    def test_time_tracking_project_url(self):
        self.check_url_returns_view("/projects/199/", core_views.time_projects)


    def test_time_tracking_projects_url(self):
        self.check_url_returns_view("/projects/", core_views.projects)
