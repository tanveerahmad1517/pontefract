from .base import FunctionalTest

class SignupTests(FunctionalTest):

    def test_can_make_account(self):
        # User goes to the website
        self.get("/")

        # The name is prominently displayed
        h1 = self.browser.find_element_by_tag_name("h1")
        self.assertEqual(h1.text, "pontefract")

        # There is a brief description
        description = self.browser.find_element_by_id("site-description")
        self.assertIn("time tracking for individuals", description.text.lower())
