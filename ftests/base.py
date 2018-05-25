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
def dt(year, month, day, hour, min=0, sec=0, tz=AUCK):
    return tz.localize(datetime(year, month, day, hour, min, sec))

class FunctionalTest(StaticLiveServerTestCase, BrowserTest):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.freezer = freeze_time("1997-05-1 15:00:00") #UTC time
        self.freezer.start()

        self.user = User.objects.create_user(
         username="sarah", email="sarah@gmail.com",
         timezone="Pacific/Auckland", password="password"
        )
        timezone.activate(self.user.timezone)

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
        Session.objects.create(
         start=dt(1997, 5, 1, 15, 30), timezone=AUCK,
         end=dt(1997, 5, 1, 16, 10), project=self.research
        )

        Session.objects.create(
         start=dt(1997, 4, 21, 15, 20), timezone=AUCK, breaks=5,
         end=dt(1997, 4, 21, 16), project=self.teaching
        )
        Session.objects.create(
         start=dt(1997, 4, 21, 20, 5), timezone=AUCK, breaks=15,
         end=dt(1997, 4, 21, 21), project=self.coding
        )
        Session.objects.create(
         start=dt(1997, 4, 2, 12, 0), timezone=AUCK,
         end=dt(1997, 4, 2, 12, 10), project=self.fencing
        )

        Session.objects.create(
         start=dt(1996, 12, 24, 15, 20), timezone=AUCK, breaks=5,
         end=dt(1996, 12, 24, 16), project=self.cycling
        )
        Session.objects.create(
         start=dt(1996, 12, 24, 20, 5), timezone=AUCK, breaks=15,
         end=dt(1996, 12, 24, 21), project=self.running
        )
        Session.objects.create(
         start=dt(1996, 12, 24, 12, 0), timezone=AUCK,
         end=dt(1996, 12, 24, 12, 10), project=self.gym
        )
        Session.objects.create(
         start=dt(1996, 12, 24, 19, 0), timezone=AUCK,
         end=dt(1996, 12, 24, 20, 10), project=self.research
        )

        user2 = User.objects.create_user(
         username="Kurt", email="kurt@gmail.com",
         timezone="Canada/Pacific", password="password"
        )
        self.running2 = Project.objects.create(name="Running", user=user2)
        PAC = pytz.timezone("Canada/Pacific")
        Session.objects.create(
         start=dt(1997, 5, 1, 2, 30, tz=PAC), timezone=PAC, breaks=5,
         end=dt(1997, 5, 2, 2, 40, tz=PAC), project=self.running2
        )


    def tearDown(self):
        Session.objects.all().delete()
        Project.objects.all().delete()
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
        self.sleep(0.2)
