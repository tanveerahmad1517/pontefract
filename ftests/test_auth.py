from .base import FunctionalTest
from datetime import datetime
from time import sleep

class SignupTests(FunctionalTest):

    def test_can_sign_up(self):
        # The user goes to the main page
        self.get("/")

        # There is a nav and a main section
        nav = self.browser.find_element_by_tag_name("nav")
        main = self.browser.find_element_by_tag_name("main")

        # There is a form for signing up in the main section
        form = main.find_element_by_tag_name("form")
        username_input = form.find_element_by_id("username")
        email_input = form.find_element_by_id("email")
        password_input = form.find_element_by_id("password")
        submit_button = form.find_elements_by_tag_name("input")[-1]

        # They signup
        username_input.send_keys("malotru69")
        email_input.send_keys("blazeit1337@outlook.com")
        password_input.send_keys("password1")
        submit_button.click()

        # They are on the main page, logged in
        self.check_page("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("malotru69", nav.text)
        self.assertIn("Log Out", nav.text)

        # They logout
        logout = nav.find_element_by_id("logout-link").find_element_by_tag_name("a")
        logout.click()
        self.check_page("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertNotIn("malotru69", nav.text)

        # They log back in
        login = nav.find_element_by_id("login")
        name_input, password_input = login.find_elements_by_tag_name("input")[:2]
        name_input.send_keys("malotru69")
        password_input.send_keys("password1")
        submit_button = login.find_elements_by_tag_name("input")[-1]
        submit_button.click()

        # They are on the main page, logged in
        self.check_page("/")
        nav = self.browser.find_element_by_tag_name("nav")
        self.assertIn("malotru69", nav.text)
        self.assertIn("Log Out", nav.text)


    def test_cannot_sign_up_with_exsisting_email(self):
        pass


    def test_cannot_sign_up_with_exsisting_username(self):
        pass



class LoginTests(FunctionalTest):

    def test_can_login(self):
        pass


    def test_incorrect_login(self):
        pass



class LogoutTests(FunctionalTest):

    def test_can_logout(self):
        pass



class AccountDeletionTests(FunctionalTest):

    def test_can_delete_account(self):
        pass
