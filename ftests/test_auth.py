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
        today = self.browser.find_element_by_class_name("day-sessions")
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

    def test_can_view_profile(self):
        # User goes to their account page
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        self.check_title("sarah")

        # There is a user div with the profile selected
        user_div = self.browser.find_element_by_id("user")
        sections = user_div.find_elements_by_class_name("section")
        self.assertIn("selected", sections[0].get_attribute("class"))
        for section in sections[1:]:
            self.assertNotIn("selected", section.get_attribute("class"))

        # The user's details are there
        info = user_div.find_element_by_id("user-settings")
        self.assertIn("Username: sarah", info.text)
        self.assertIn("Signed Up: Thursday 1 May, 1997", info.text)
        self.assertIn("Projects: 8", info.text)
        self.assertIn("Hours logged: 6 hours, 40 minutes", info.text)


    def test_can_change_timezone(self):
        # User goes to their time settings page
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        sections = self.browser.find_elements_by_class_name("section")
        self.click(sections[1])
        self.check_page("/profile/time/")

        # There is a dropdown for timezone
        form = self.browser.find_element_by_class_name("settings-form")
        timezone = form.find_element_by_id("id_timezone")
        self.assertEqual(self.get_select_value(timezone), "Pacific/Auckland")

        # They change it
        self.select_dropdown(timezone, "Europe/Istanbul")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/time/")
        self.check_title("sarah")
        timezone = self.browser.find_element_by_id("id_timezone")
        self.assertEqual(self.get_select_value(timezone), "Europe/Istanbul")

        # The timezone has really changed
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.assertIn("Thursday 1 May, 1997", today.text)


    def test_can_change_project_order(self):
        # User goes to their time settings page
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        sections = self.browser.find_elements_by_class_name("section")
        self.click(sections[1])
        self.check_page("/profile/time/")

        # There is a dropdown for project order
        form = self.browser.find_element_by_class_name("settings-form")
        project_order = form.find_element_by_id("id_project_order")
        self.assertEqual(self.get_select_value(project_order), "TD")

        # They change it
        self.select_dropdown(project_order, "Last Done")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/time/")
        self.check_title("sarah")
        project_order = self.browser.find_element_by_id("id_project_order")
        self.assertEqual(self.get_select_value(project_order), "LD")

        # The order has really changed
        self.get("/projects/")
        names = [n.text for n in self.browser.find_elements_by_class_name("project-name")]
        self.assertEqual(names, [
         "Yoga", "Research", "Coding", "Teaching", "Fencing", "Running", "Cycling", "Gym"
        ])


    def test_can_change_email_address(self):
        # User goes to their time settings page
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        sections = self.browser.find_elements_by_class_name("section")
        self.click(sections[2])
        self.check_page("/profile/account/")

        # There is an input for email
        form = self.browser.find_element_by_class_name("settings-form")
        email = form.find_element_by_id("id_email")
        self.assertEqual(email.get_attribute("value"), "sarah@gmail.com")

        # They change it and enter their password
        email.clear(); email.send_keys("sarah@sarah.com")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("password")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/account/")

        # The email has changed
        self.get("/profile/account/")
        email = self.browser.find_element_by_id("id_email")
        self.assertEqual(email.get_attribute("value"), "sarah@sarah.com")


    def test_need_password_to_change_email_address(self):
        # User goes to their time settings page
        self.login()
        self.get("/profile/account/")

        # They enter a new email and a wrong password
        form = self.browser.find_element_by_class_name("settings-form")
        email = form.find_element_by_id("id_email")
        email.clear(); email.send_keys("sarah@sarah.com")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("passwordX")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)

        # It doesn't work
        self.check_page("/profile/account/")
        form = self.browser.find_element_by_class_name("settings-form")
        email = form.find_element_by_id("id_email")
        self.assertEqual(email.get_attribute("value"), "sarah@sarah.com")
        current_password = form.find_element_by_id("id_current_password")
        self.assertFalse(current_password.get_attribute("value"))
        error = form.find_element_by_id("current-password-error")
        self.assertIn("valid", error.text)
        self.get("/profile/account/")
        email = self.browser.find_element_by_id("id_email")
        self.assertEqual(email.get_attribute("value"), "sarah@gmail.com")


    def test_can_change_password(self):
        # User goes to their time settings page
        self.login()
        link = self.browser.find_element_by_id("account-link")
        self.click(link)
        self.check_page("/profile/")
        sections = self.browser.find_elements_by_class_name("section")
        self.click(sections[2])
        self.check_page("/profile/account/")

        # There are inputs for passwords
        form = self.browser.find_element_by_class_name("settings-form")
        password1 = form.find_element_by_id("id_new_password")
        password2 = form.find_element_by_id("id_confirm_password")

        # They enter a new password and confirm
        password1.send_keys("betterpassword")
        password2.send_keys("betterpassword")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("password")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/account/")

        # The password has changed
        self.logout()
        self.get("/login/")
        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")
        username.send_keys("sarah")
        password.send_keys("password")
        self.click(self.browser.find_elements_by_tag_name("input")[-1])
        self.check_page("/login/")
        password = self.browser.find_element_by_id("id_password")
        password.send_keys("betterpassword")
        self.click(self.browser.find_elements_by_tag_name("input")[-1])
        self.check_title("Home")


    def test_passwords_must_match_to_change(self):
        # User goes to their time settings page
        self.login()
        self.get("/profile/account/")

        # There are inputs for passwords
        form = self.browser.find_element_by_class_name("settings-form")
        password1 = form.find_element_by_id("id_new_password")
        password2 = form.find_element_by_id("id_confirm_password")

        # They enter a new password and confirm
        password1.send_keys("betterpassword")
        password2.send_keys("betterpasswordX")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("password")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/account/")

        # It doesn't work
        self.check_page("/profile/account/")
        form = self.browser.find_element_by_class_name("settings-form")
        error = form.find_element_by_id("password-error")
        self.assertIn("match", error.text)
        self.logout()
        self.get("/login/")
        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")
        username.send_keys("sarah")
        password.send_keys("password")
        self.click(self.browser.find_elements_by_tag_name("input")[-1])
        self.check_title("Home")


    def test_passwords_must_be_long_enough(self):
        # User goes to their time settings page
        self.login()
        self.get("/profile/account/")

        # There are inputs for passwords
        form = self.browser.find_element_by_class_name("settings-form")
        password1 = form.find_element_by_id("id_new_password")
        password2 = form.find_element_by_id("id_confirm_password")

        # They enter a new password and confirm
        password1.send_keys("psswd")
        password2.send_keys("psswd")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("password")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)
        self.check_page("/profile/account/")

        # It doesn't work
        self.check_page("/profile/account/")
        form = self.browser.find_element_by_class_name("settings-form")
        error = form.find_element_by_id("password-error")
        self.assertIn("8 characters", error.text)
        self.logout()
        self.get("/login/")
        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")
        username.send_keys("sarah")
        password.send_keys("password")
        self.click(self.browser.find_elements_by_tag_name("input")[-1])
        self.check_title("Home")


    def test_need_password_to_change_password(self):
        # User goes to their time settings page
        self.login()
        self.get("/profile/account/")

        # They enter a new email and a wrong password
        form = self.browser.find_element_by_class_name("settings-form")
        password1 = form.find_element_by_id("id_new_password")
        password2 = form.find_element_by_id("id_confirm_password")
        password1.send_keys("betterpassword")
        password2.send_keys("betterpassword")
        current_password = form.find_element_by_id("id_current_password")
        current_password.send_keys("passwordX")
        save = form.find_elements_by_tag_name("input")[-1]
        self.click(save)

        # It doesn't work
        self.check_page("/profile/account/")
        form = self.browser.find_element_by_class_name("settings-form")
        current_password = form.find_element_by_id("id_current_password")
        self.assertFalse(current_password.get_attribute("value"))
        error = form.find_element_by_id("current-password-error")
        self.assertIn("valid", error.text)
        self.logout()
        self.get("/login/")
        username = self.browser.find_element_by_id("id_username")
        password = self.browser.find_element_by_id("id_password")
        username.send_keys("sarah")
        password.send_keys("password")
        self.click(self.browser.find_elements_by_tag_name("input")[-1])
        self.check_title("Home")

        

    '''def test_can_delete_account(self):
        # User goes to their account page

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
        self.assertIn("credentials", error.text)'''


    def test_profile_page_protection(self):
        for page in ["/", "/time/", "/account/"]:
            self.get(f"/profile{page}")
            self.check_page("/")
