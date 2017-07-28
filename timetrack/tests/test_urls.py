from pontefract.tests import UrlTest
from timetrack import views

class UsersUrlTests(UrlTest):

    def test_root_url_resolves_to_home_page(self):
        self.check_url_returns_view("/", views.home_page)
