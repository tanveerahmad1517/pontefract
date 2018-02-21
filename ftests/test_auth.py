from .base import FunctionalTest
from django.contrib.auth.models import User

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


    def test_usernames_must_be_unique(self):
        User.objects.create_user(
         username="user",
         email="a@b.com",
         password="password"
        )

        # User goes to the landing page
        self.get("/")

        # They enter details with a taken username
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        username.send_keys("user")
        email.send_keys("joe@gmail.com")
        password1.send_keys("swordfish")
        password2.send_keys("swordfish")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are still on the landing page and an error message is there
        self.check_page("/")
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(username.get_attribute("value"), "user")
        self.assertEqual(email.get_attribute("value"), "joe@gmail.com")
        self.assertEqual(password1.get_attribute("value"), "")
        self.assertEqual(password2.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("already", error.text)


    def test_emails_must_be_unique(self):
        User.objects.create_user(
         username="user",
         email="a@b.com",
         password="password"
        )

        # User goes to the landing page
        self.get("/")

        # They enter details with a taken email
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        username.send_keys("joe23")
        email.send_keys("a@b.com")
        password1.send_keys("swordfish")
        password2.send_keys("swordfish")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are still on the landing page and an error message is there
        self.check_page("/")
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(username.get_attribute("value"), "joe23")
        self.assertEqual(email.get_attribute("value"), "a@b.com")
        self.assertEqual(password1.get_attribute("value"), "")
        self.assertEqual(password2.get_attribute("value"), "")
        error = form.find_element_by_id("email-error")
        self.assertIn("already", error.text)
