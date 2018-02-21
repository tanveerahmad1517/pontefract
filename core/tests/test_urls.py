from testarsenal import DjangoTest
import core.views as core_views
import users.views as user_views

class UrlTests(DjangoTest):

    def test_root_url(self):
        self.check_url_returns_view("/", core_views.root)


    def test_signup_url(self):
        self.check_url_returns_view("/signup/", user_views.signup)
