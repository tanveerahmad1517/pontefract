from django.contrib.auth.models import User
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


    def test_username_must_be_unique(self):
        User.objects.create_user(
         username="user",
         email="a@b.com",
         password="password"
        )
        self.get("/")

        # There is a signup form
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        submit = form.find_elements_by_tag_name("input")[-1]

        # They enter some details and submit
        username_input.send_keys("user")
        email_input.send_keys("x@b.com")
        password_input.send_keys("tonks23")
        password2_input.send_keys("tonks23")
        self.click(submit)

        # They are still on the signup page and there is an error
        self.check_page("/")
        overview = self.browser.find_element_by_id("overview")
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(username_input.get_attribute("value"), "user")
        self.assertEqual(email_input.get_attribute("value"), "x@b.com")
        self.assertEqual(password_input.get_attribute("value"), "")
        self.assertEqual(password2_input.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("already", error.text)


    def test_email_must_be_unique(self):
        User.objects.create_user(
         username="user",
         email="a@b.com",
         password="password"
        )
        self.get("/")

        # There is a signup form
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        submit = form.find_elements_by_tag_name("input")[-1]

        # They enter some details and submit
        username_input.send_keys("user2")
        email_input.send_keys("a@b.com")
        password_input.send_keys("tonks23")
        password2_input.send_keys("tonks23")
        self.click(submit)

        # They are still on the signup page and there is an error
        self.check_page("/")
        overview = self.browser.find_element_by_id("overview")
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(username_input.get_attribute("value"), "user2")
        self.assertEqual(email_input.get_attribute("value"), "a@b.com")
        self.assertEqual(password_input.get_attribute("value"), "")
        self.assertEqual(password2_input.get_attribute("value"), "")
        error = form.find_element_by_id("email-error")
        self.assertIn("already", error.text)


    def test_password_must_match(self):
        self.get("/")

        # There is a signup form
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        submit = form.find_elements_by_tag_name("input")[-1]

        # They enter some details and submit
        username_input.send_keys("user")
        email_input.send_keys("x@b.com")
        password_input.send_keys("tonks23")
        password2_input.send_keys("tonks24")
        self.click(submit)

        # They are still on the signup page and there is an error
        self.check_page("/")
        overview = self.browser.find_element_by_id("overview")
        form = self.browser.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        password_input = form.find_elements_by_tag_name("input")[2]
        password2_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(username_input.get_attribute("value"), "user")
        self.assertEqual(email_input.get_attribute("value"), "x@b.com")
        self.assertEqual(password_input.get_attribute("value"), "")
        self.assertEqual(password2_input.get_attribute("value"), "")
        error = form.find_element_by_id("password-error")
        self.assertIn("don't match", error.text)
