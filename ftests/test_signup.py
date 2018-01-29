from .base import FunctionalTest

class SignupTests(FunctionalTest):

    def test_can_make_account(self):
        self.get("/")

        # They are on the signup page
        self.check_title("Sign Up")
        self.check_h1("Pontefract")

        # There is a div giving an overview of the app
        overview = self.browser.find_element_by_id("overview")
        self.assertIn("pontefract", overview.text.lower())
        self.assertIn("time tracking", overview.text.lower())
