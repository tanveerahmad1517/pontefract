from selenium import webdriver
from testarsenal import BrowserTest
from core.models import User
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.user = User.objects.create_user(
         username="sarah",
         email="sarah@gmail.com",
         timezone="Pacific/Auckland",
         password="password"
        )
        timezone.activate(self.user.timezone)


    def tearDown(self):
        self.browser.close()


    def login(self):
        self.client.login(username="sarah", password="password")
        cookie = self.client.cookies["sessionid"].value
        self.browser.get(self.live_server_url + "/")
        self.browser.add_cookie({
         "name": "sessionid", "value": cookie, "secure": False, "path": "/"
        })
        self.browser.refresh()


    def logout(self):
        self.browser.get(self.live_server_url + "/")
        self.click(self.browser.find_element_by_id("logout-link"))
