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

        # There is a signup form
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        submit = form.find_elements_by_tag_name("input")[-1]

        # They enter some details and submit
        username_input.send_keys("lupin")
        email_input.send_keys("remus.l@hogwarts.ac.uk")
        password_input.send_keys("tonks23")
        password2_input.send_keys("tonks23")
        self.click(submit)

        # They are still on the root page but it's not the welcome page
        self.check_page("/")
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("overview")

        # Their username is in the header
        header = self.browser.find_element_by_tag_name("header")
        self.assertIn("lupin", header.text)
