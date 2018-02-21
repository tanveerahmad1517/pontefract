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

        # There is a form to signup
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]

        # They enter their details
        username.send_keys("joe23")
        email.send_keys("joe@gmail.com")
        password1.send_keys("swordfish")
        password2.send_keys("swordfish")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are on their own homepage
        self.check_page("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("joe23", nav.text)
