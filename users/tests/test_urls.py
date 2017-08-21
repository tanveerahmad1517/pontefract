from pontefract.tests import UrlTest
from users import views

class UsersUrlTests(UrlTest):

    def test_logout_url_resolves_to_logout_page(self):
        self.check_url_returns_view("/logout/", views.logout_page)
