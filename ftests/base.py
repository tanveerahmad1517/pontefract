from selenium import webdriver
from datetime import datetime
import pytz
from freezegun import freeze_time
from testarsenal import BrowserTest
from core.models import User
from projects.models import *
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

AUCK = pytz.timezone("Pacific/Auckland")
def dt(year, month, day, hour, min=0, sec=0):
    return AUCK.localize(datetime(year, month, day, hour, min, sec))

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.browser = webdriver.Chrome()

        self.user = User.objects.create_user(
         username="sarah", email="sarah@gmail.com",
         timezone="Pacific/Auckland", password="password"
        )

        self.research = Project.objects.create(name="Research", user=self.user)
        self.cycling = Project.objects.create(name="Cycling", user=self.user)
        self.fencing = Project.objects.create(name="Fencing", user=self.user)
        self.running = Project.objects.create(name="Running", user=self.user)
        self.yoga = Project.objects.create(name="Yoga", user=self.user)
        self.teaching = Project.objects.create(name="Teaching", user=self.user)
        self.coding = Project.objects.create(name="Coding", user=self.user)
        self.gym = Project.objects.create(name="Gym", user=self.user)


        Session.objects.create(
         start=dt(1997, 5, 2, 0, 30), timezone=AUCK, breaks=5,
         end=dt(1997, 5, 2, 0, 55), project=self.research
        )
        Session.objects.create(
         start=dt(1997, 5, 2, 1), timezone=AUCK,
         end=dt(1997, 5, 2, 2), project=self.yoga
        )

        Session.objects.create(
         start=dt(1997, 5, 1, 23, 30), timezone=AUCK,
         end=dt(1997, 5, 2, 0, 10), project=self.research
        )

        self.freezer = freeze_time("1997-05-1 15:00:00") #UTC time
        self.freezer.start()
        timezone.activate(self.user.timezone)


    def tearDown(self):
        self.freezer.stop()
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
