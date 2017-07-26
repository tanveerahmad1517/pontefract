from pontefract.tests import UrlTest
from users import views

class UsersUrlTests(UrlTest):

    def test_root_url_resolves_to_signup_page(self):
        self.check_url_returns_view("/", views.signup_page)
