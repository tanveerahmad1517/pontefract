import pytz
from datetime import datetime
from core.models import User
from .base import FunctionalTest

class SignupTests(FunctionalTest):

    def fill_in_signup_form(self, username, email, timezone, password, pass2=None):
        # There is a form to signup
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        username_input = form.find_elements_by_tag_name("input")[0]
        email_input = form.find_elements_by_tag_name("input")[1]
        timezone_input = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]

        # They enter their details
        username_input.send_keys(username)
        email_input.send_keys(email)
        self.select_dropdown(timezone_input, timezone)
        password1.send_keys(password)
        password2.send_keys(pass2 if pass2 else password)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)


    def check_signup_form(self, username_value=None, username_error=None,
     email_value=None, email_error=None, password_error=None):
        # There is a form to signup
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        timezone = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]

        # It looks ok
        if username_value:
            self.assertEqual(username.get_attribute("value"), username_value)
        if email_value:
            self.assertEqual(email.get_attribute("value"), email_value)
        if username_error:
            error = form.find_element_by_id("username-error")
            self.assertIn(username_error, error.text)
        if email_error:
            error = form.find_element_by_id("email-error")
            self.assertIn(email_error, error.text)
        if password_error:
            error = form.find_element_by_id("password-error")
            self.assertIn(password_error, error.text)
        self.assertEqual(password1.get_attribute("value"), "")
        self.assertEqual(password2.get_attribute("value"), "")


    def test_can_make_account(self):
        # User goes to the website
        self.get("/")

        # The name is prominently displayed
        self.check_title("pontefract")
        self.check_h1("pontefract")

        # There is a brief description
        description = self.browser.find_element_by_id("site-description")
        self.assertIn("time tracking for individuals", description.text.lower())

        # They enter their details in the signup form
        self.fill_in_signup_form(
         "joe23", "joe@gmail.com", "Pacific/Auckland", "swordfish"
        )

        # They are on their own homepage
        self.check_page("/")
        self.check_title("Home")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("joe23", nav.text)

        # There is a starter section for time tracking
        now = datetime.now(tz=pytz.timezone("Pacific/Auckland"))
        time = self.browser.find_element_by_id("time-tracking")
        new_session = time.find_element_by_tag_name("form")
        today = time.find_element_by_class_name("day-time-tracking")
        self.assertIn("0 minutes", today.text)
        self.assertIn("Friday 2 May, 1997", today.text)
        self.assertIn("no sessions", today.text)
        sessions = today.find_elements_by_class_name("session")
        self.assertEqual(len(sessions), 0)
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_class_name("month-link")


    def test_usernames_must_be_unique(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with a taken username
        self.fill_in_signup_form(
         "sarah", "joe@gmail.com", "Pacific/Auckland", "swordfish"
        )

        # They are still on the landing page and an error message is there
        self.check_page("/")
        self.check_signup_form(
         username_value="sarah", email_value="joe@gmail.com",
         username_error="already"
        )


    def test_username_must_be_slug(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with a taken username
        self.fill_in_signup_form(
         "joe jones", "joe@gmail.com", "Pacific/Auckland", "swordfish"
        )

        # They are still on the landing page and an error message is there
        self.check_page("/")
        self.check_signup_form(
         username_value="joe jones", email_value="joe@gmail.com",
         username_error="valid"
        )


    def test_emails_must_be_unique(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with a taken username
        self.fill_in_signup_form(
         "joe23", "sarah@gmail.com", "Pacific/Auckland", "swordfish"
        )

        # They are still on the landing page and an error message is there
        self.check_page("/")
        self.check_signup_form(
         username_value="joe23", email_value="sarah@gmail.com",
         email_error="already"
        )


    def test_passwords_must_match(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with differing passwords
        self.fill_in_signup_form(
         "joe23", "joe@gmail.com", "Pacific/Auckland", "swordfish", "swordfish2"
        )

        # They are still on the landing page and an error message is there
        self.check_page("/")
        self.check_signup_form(
         username_value="joe23", email_value="joe@gmail.com",
         password_error="don't match"
        )


    def test_password_must_be_long_enough(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with differing passwords
        self.fill_in_signup_form(
         "joe23", "joe@gmail.com", "Pacific/Auckland", "1234567", "1234567"
        )

        # They are still on the landing page and an error message is there
        self.check_page("/")
        self.check_signup_form(
         username_value="joe23", email_value="joe@gmail.com",
         password_error="8 characters"
        )



class LoginTests(FunctionalTest):

    def test_user_can_login(self):
        # The user goes to the landing page
        self.get("/")

        # The signup form has a link to login
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        login_link = form.find_elements_by_tag_name("a")[-1]

        # They click it and go to the login page
        self.click(login_link)
        self.check_page("/login/")

        # There is a link back to the signup page
        form = self.browser.find_element_by_tag_name("form")
        link = form.find_element_by_tag_name("a")
        self.click(link)
        self.check_page("/")
        self.browser.back()

        # There is a form, which they fill in
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        username.send_keys("sarah")
        password.send_keys("password")
        submit = form.find_elements_by_tag_name("input")[-1]

        # They submit and are logged in
        self.click(submit)
        self.check_page("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("sarah", nav.text)


    def test_can_reject_bad_credentials(self):
        # User goes to the login page
        self.get("/")
        signup = self.browser.find_element_by_id("signup-panel")
        form = signup.find_element_by_tag_name("form")
        login_link = form.find_elements_by_tag_name("a")[-1]
        self.click(login_link)
        self.check_page("/login/")

        # They put incorrect credentials in
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        username.send_keys("sarah")
        password.send_keys("psswrd")
        submit = form.find_elements_by_tag_name("input")[-1]

        # They don't work
        self.click(submit)
        self.check_page("/login/")
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        self.assertEqual(username.get_attribute("value"), "sarah")
        self.assertEqual(password.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("credentials", error.text)



class LogoutTests(FunctionalTest):

    def test_can_logout(self):
        # The user goes to their home page
        self.login()
        self.get("/")

        # They can log out
        nav = self.browser.find_element_by_tag_name("nav")
        logout_link = nav.find_element_by_id("logout-link")
        self.click(logout_link)
        self.check_page("/")
        signup = self.browser.find_element_by_id("signup-panel")



class AccountModificationTests(FunctionalTest):

    def test_can_delete_account(self):
        # User goes to their account page
        User.objects.create_user(
         username="bill",
         email="bill@gmail.com",
         timezone="Pacific/Auckland",
         password="password_"
        )
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        self.check_title("sarah")

        # There is a section for deleting an account
        deletion = self.browser.find_element_by_id("account-deletion")
        button = deletion.find_element_by_class_name("delete-link")
        self.click(button)
        self.check_page("/delete-account/")
        self.check_title("Delete Account")

        # They enter their credentials incorrectly on the page
        form = self.browser.find_elements_by_tag_name("form")[1]
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        username.send_keys("bill")
        password.send_keys("password_")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # The account is not deleted
        self.check_page("/delete-account/")
        form = self.browser.find_elements_by_tag_name("form")[1]
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        self.assertEqual(username.get_attribute("value"), "bill")
        self.assertEqual(password.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("credentials", error.text)

        # They enter the correct details and delete
        username.clear()
        username.send_keys("sarah")
        password.send_keys("password")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)
        self.check_page("/")
        self.check_h1("pontefract")
        self.get("/login/")
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        username.send_keys("sarah")
        password.send_keys("password")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)
        self.check_page("/login/")
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        self.assertEqual(username.get_attribute("value"), "sarah")
        self.assertEqual(password.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("credentials", error.text)


    def test_profile_page_protection(self):
        self.get("/profile/")
        self.check_page("/")
        self.get("/delete-account/")
        self.check_page("/")


    def test_can_change_timezone(self):
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        self.check_title("sarah")

        # There is a dropdown for timezone
        form = self.browser.find_element_by_id("settings-form")
        timezone = form.find_element_by_id("id_timezone")
        self.assertEqual(self.get_select_value(timezone), "Pacific/Auckland")

        # They change it
        self.select_dropdown(timezone, "Europe/Istanbul")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/")
        self.check_title("sarah")
        timezone = self.browser.find_element_by_id("id_timezone")
        self.assertEqual(self.get_select_value(timezone), "Europe/Istanbul")
