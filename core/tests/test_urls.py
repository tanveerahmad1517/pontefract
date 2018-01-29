from testarsenal import DjangoTest
import core.views as views

class UrlTests(DjangoTest):

    def test_root_url(self):
        self.check_url_returns_view("/", views.root)
