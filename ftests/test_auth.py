import pytz
from datetime import datetime
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
        timezone = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]

        # They enter their details
        username.send_keys("joe23")
        email.send_keys("joe@gmail.com")
        self.select_dropdown(timezone, "Pacific/Auckland")
        password1.send_keys("swordfish")
        password2.send_keys("swordfish")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are on their own homepage
        now = datetime.now(tz=pytz.timezone("Pacific/Auckland"))
        self.check_page("/")
        self.check_title("Home")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("joe23", nav.text)

        # There is a starter section for time tracking
        time = self.browser.find_element_by_id("user-time-tracking")
        self.assertEqual(time.find_element_by_tag_name("h2").text, "Time Tracking")
        new_session = time.find_element_by_tag_name("form")
        today = time.find_element_by_class_name("day-time-tracking")
        self.assertIn("0 minutes", today.text)
        self.assertIn(str(now.year), today.text)
        self.assertIn(str(now.day), today.text)
        self.assertIn(str(now.strftime("%B")), today.text)
        sessions = today.find_elements_by_class_name("session")
        self.assertEqual(len(sessions), 0)
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_class_name("projects-link")
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_class_name("month-link")


    def test_usernames_must_be_unique(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with a taken username
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        timezone = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        username.send_keys("sarah")
        email.send_keys("joe@gmail.com")
        self.select_dropdown(timezone, "Pacific/Auckland")
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
        self.assertEqual(username.get_attribute("value"), "sarah")
        self.assertEqual(email.get_attribute("value"), "joe@gmail.com")
        self.assertEqual(password1.get_attribute("value"), "")
        self.assertEqual(password2.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("already", error.text)


    def test_emails_must_be_unique(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with a taken email
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        timezone = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        username.send_keys("joe23")
        email.send_keys("sarah@gmail.com")
        self.select_dropdown(timezone, "Pacific/Auckland")
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
        self.assertEqual(email.get_attribute("value"), "sarah@gmail.com")
        self.assertEqual(password1.get_attribute("value"), "")
        self.assertEqual(password2.get_attribute("value"), "")
        error = form.find_element_by_id("email-error")
        self.assertIn("already", error.text)


    def test_passwords_must_match(self):
        # User goes to the landing page
        self.get("/")

        # They enter details with differing passwords
        form = self.browser.find_element_by_tag_name("form")
        username = form.find_elements_by_tag_name("input")[0]
        email = form.find_elements_by_tag_name("input")[1]
        timezone = form.find_element_by_tag_name("select")
        password1 = form.find_elements_by_tag_name("input")[2]
        password2 = form.find_elements_by_tag_name("input")[3]
        username.send_keys("joe23")
        email.send_keys("a@b.com")
        self.select_dropdown(timezone, "Pacific/Auckland")
        password1.send_keys("swordfish")
        password2.send_keys("swordfishx")
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
        error = form.find_element_by_id("password-error")
        self.assertIn("don't match", error.text)



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
        self.login()
        link = self.browser.find_element_by_class_name("account-link")
        self.click(link)
        self.check_page("/profile/")
        self.check_title("sarah")
        self.check_h1("sarah")

        # There is a section for deleting an account
        deletion = self.browser.find_element_by_id("account-deletion")
        button = deletion.find_element_by_class_name("delete-button")
        self.click(button)
        self.check_page("/delete-account/")
        self.check_title("Delete Account")
        self.check_h1("Delete Account")

        # They enter their credentials incorrectly on the page
        form = self.browser.find_elements_by_tag_name("form")[1]
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        username.send_keys("sarah")
        password.send_keys("wrongpassword")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # The account is not deleted
        self.check_page("/delete-account/")
        form = self.browser.find_elements_by_tag_name("form")[1]
        username = form.find_elements_by_tag_name("input")[0]
        password = form.find_elements_by_tag_name("input")[1]
        self.assertEqual(username.get_attribute("value"), "sarah")
        self.assertEqual(password.get_attribute("value"), "")
        error = form.find_element_by_id("username-error")
        self.assertIn("credentials", error.text)

        # They enter the correct details and delete
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
        link = self.browser.find_element_by_class_name("account-link")
        self.click(link)
        self.check_page("/profile/")
        self.check_title("sarah")
        self.check_h1("sarah")

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
        self.check_h1("sarah")
        timezone = self.browser.find_element_by_id("id_timezone")
        self.assertEqual(self.get_select_value(timezone), "Europe/Istanbul")
