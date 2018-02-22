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
         password="passwords"
        )


    def tearDown(self):
        self.browser.close()
