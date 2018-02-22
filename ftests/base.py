from selenium import webdriver
from testarsenal import BrowserTest
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.browser = webdriver.Chrome()
        User.objects.create_user(
         username="sarah",
         email="sarah@gmail.com",
         password="password"
        )


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
