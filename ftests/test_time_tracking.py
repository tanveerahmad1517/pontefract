from datetime import datetime, date
import pytz
from selenium.webdriver.common.keys import Keys
from django.utils import timezone
from projects.models import Project, Session
from core.models import User
from freezegun import freeze_time
from .base import FunctionalTest

class TimeTrackingTests(FunctionalTest):

    def fill_in_session_form(self, start_time, end_time, breaks,
     project, existing=False, start_day=None, end_day=None):
        # There is a form to record work
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        with self.assertRaises(self.NoElement):
            form.find_element_by_tag_name("select")
        now_buttons = form.find_elements_by_class_name("now-button")

        # They enter some values and submit
        if start_day:
            self.browser.execute_script(
             "arguments[0].value = '{}';".format(start_day), start_day_input
            )
        self.browser.execute_script(
         "arguments[0].value = '{}';".format(start_time), start_time_input
        )
        if end_day:
            self.browser.execute_script(
             "arguments[0].value = '{}';".format(end_day), end_day_input
            )
        self.browser.execute_script(
         "arguments[0].value = '{}';".format(end_time), end_time_input
        )
        breaks_input.clear()
        if breaks != "0": breaks_input.send_keys(breaks)
        project_input.clear()
        if existing:
            visible_suggestions = self.browser.find_elements_by_class_name("ui-menu-item")
            self.assertEqual(len(visible_suggestions), 0)
            project_input.send_keys(project[:3])
            self.sleep(0.6)
            visible_suggestions = self.browser.find_elements_by_class_name("ui-menu-item")
            self.assertGreater(len(visible_suggestions), 0)
            for suggestion in visible_suggestions:
                if suggestion.text == project:
                    suggestion.click()
                    break
            self.assertEqual(project_input.get_attribute("value"), project)
        else:
            project_input.send_keys(project)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)


    def check_session_form(self, start_day=None, start_time=None, end_day=None,
     end_time=None, breaks=None, project=None, start_error=None, end_error=None,
     breaks_error=None, project_error=None):
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        if start_day:
            self.assertEqual(start_day_input.get_attribute("value"), start_day)
        if start_time:
            self.assertEqual(start_time_input.get_attribute("value"), start_time)
        if end_day:
            self.assertEqual(end_day_input.get_attribute("value"), end_day)
        if end_time:
            self.assertEqual(end_time_input.get_attribute("value"), end_time)
        if breaks:
            self.assertEqual(breaks_input.get_attribute("value"), breaks)
        if project:
            self.assertEqual(project_input.get_attribute("value"), project)
        if start_error:
            error = form.find_element_by_id("start-error")
            self.assertIn(start_error, error.text)
        if end_error:
            error = form.find_element_by_id("end-error")
            self.assertIn(end_error, error.text)
        if breaks_error:
            error = form.find_element_by_id("breaks-error")
            self.assertIn(breaks_error, error.text)
        if project_error:
            error = form.find_element_by_id("project-error")
            self.assertIn(project_error, error.text)


    def check_day_report(self, div, total, sessions, date=None):
        if date:
            self.assertIn(date, div.find_element_by_class_name("date").text)
        self.assertIn(total, div.find_element_by_class_name("total-time").text)
        session_divs = div.find_elements_by_class_name("session")
        self.assertEqual(len(sessions), len(session_divs))
        for session, session_div in zip(sessions, session_divs):
            cells = session_div.find_elements_by_tag_name("td")
            self.assertIn(session[0], cells[0].text)
            self.assertIn(session[1], cells[1].text)
            if session[2]:
                self.assertIn(session[2], cells[2].text)
            else:
                self.assertEqual(cells[2].text, "")



class SessionAddingTests(TimeTrackingTests):

    def test_can_add_work_session(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # There are two sessions already there
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They fill out the session form that is there
        self.check_session_form(start_day="1997-05-02", end_day="1997-05-02")
        self.fill_in_session_form("06:05", "06:35", "10", "Dog Walking")

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 40 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None],
         ["06:05 - 06:35", "Dog Walking", "20 minutes", "10 minute break"]
        ])

        # The database has the timezone in it
        self.assertEqual(
         Session.objects.last().timezone, pytz.timezone("Pacific/Auckland")
        )


    def test_can_add_work_session_to_existing_project(self):
        # The user goes to the home page and fills out the form there
        self.login()
        self.get("/")
        self.fill_in_session_form("16:05", "16:35", "0", "Cycling", existing=True)

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 50 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None],
         ["16:05 - 16:35", "Cycling", "30 minutes", None]
        ])


    def test_can_add_work_session_for_previous_day(self):
        # The user goes to the yesetrday page and fills out the form there
        self.login()
        self.get("/time/2009/10/1/")
        self.fill_in_session_form("16:05", "16:35", "0", "Cycling")

        # They are on the day's page
        self.check_page("/time/2009/10/1/")

        # The total for the day is updated
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "30 minutes", [
         ["16:05 - 16:35", "Cycling", "30 minutes", None]
        ])


    def test_second_time_must_be_after_first(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # They fill out the session form that is there
        self.fill_in_session_form("06:05", "05:05", "10", "Dog Walking")

        # They are still on the home page and there are no extra sessions
        self.check_page("/")
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="06:05", end_time="05:05", breaks="10", end_error="before"
        )


    def test_time_must_be_daylight_savings_compliant(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # They fill out the session form that is there
        self.fill_in_session_form(
         "02:30", "02:45", "", "Dog Walking", start_day="2018-09-30", end_day="2018-09-30"
        )

        # They are still on the home page and there are no extra sessions
        self.check_page("/")
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="02:30", end_time="02:45", breaks="", start_error="time zone", end_error="time zone"
        )


    def test_breaks_must_be_positive(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # They fill out the session form that is there
        self.fill_in_session_form("06:05", "07:05", "-10", "Dog Walking")

        # They are still on the home page and there are no extra sessions
        self.check_page("/")
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="06:05", end_time="07:05", breaks="-10", breaks_error="positive"
        )


    def test_breaks_must_not_cancel_out_session(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # They fill out the session form that is there
        self.fill_in_session_form("06:05", "07:05", "70", "Dog Walking")

        # They are still on the home page and there are no extra sessions
        self.check_page("/")
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="06:05", end_time="07:05", breaks="70", breaks_error="cancel"
        )


    def test_project_name_cannot_be_spaces(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # They fill out the session form that is there
        self.fill_in_session_form("06:05", "07:05", "10", "   ")

        # They are still on the home page and there are no extra sessions
        self.check_page("/")
        today = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="06:05", end_time="07:05", breaks="10", project_error="valid"
        )



class SessionViewingTests(TimeTrackingTests):

    def setUp(self):
        FunctionalTest.setUp(self)

        # Create some projects for Sarah
        running = Project.objects.create(name="Running", user=self.user)
        archery = Project.objects.create(name="Archery", user=self.user)
        cooking = Project.objects.create(name="Cooking", user=self.user)
        ultra = Project.objects.create(name="Project Ultra", user=self.user)
        reading = Project.objects.create(name="Reading", user=self.user)

        # Create some sessions for today
        tz = pytz.timezone("Pacific/Auckland")
        timezone.activate(self.user.timezone)
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 11, 0)),
         end=tz.localize(datetime(1962, 10, 27, 11, 30)),
         breaks=0, project=reading, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 12, 0)),
         end=tz.localize(datetime(1962, 10, 27, 12, 15)),
         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 9, 0)),
         end=tz.localize(datetime(1962, 10, 27, 9, 45)),
         breaks=5, project=cooking, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 18, 0)),
         end=tz.localize(datetime(1962, 10, 27, 20, 30)),
         breaks=10, project=reading, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 23, 45)),
         end=tz.localize(datetime(1962, 10, 28, 0, 30)),
         breaks=0, project=reading, timezone=tz
        )

        # Create sessions for current month
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 23, 30)),
         end=tz.localize(datetime(1962, 10, 27, 4, 30)),

         breaks=20, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 17,20)),
         end=tz.localize(datetime(1962, 10, 26, 17, 40)),

         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 6,20)),
         end=tz.localize(datetime(1962, 10, 26, 7, 40)),

         breaks=0, project=running, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 20, 9,00)),
         end=tz.localize(datetime(1962, 10, 20, 17, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 16, 9,00)),
         end=tz.localize(datetime(1962, 10, 16, 17, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 16, 18,00)),
         end=tz.localize(datetime(1962, 10, 16, 22, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 12, 9,00)),
         end=tz.localize(datetime(1962, 10, 12, 17, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 12, 18,00)),
         end=tz.localize(datetime(1962, 10, 12, 22, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 8, 9,00)),
         end=tz.localize(datetime(1962, 10, 8, 17, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 8, 18,00)),
         end=tz.localize(datetime(1962, 10, 8, 22, 00)),

         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 23,30)),
         end=tz.localize(datetime(1962, 10, 4, 4, 30)),

         breaks=20, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 17,20)),
         end=tz.localize(datetime(1962, 10, 3, 17, 40)),

         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 6,20)),
         end=tz.localize(datetime(1962, 10, 3, 7, 40)),

         breaks=0, project=running, timezone=tz
        )

        # Create sessions for previous months
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 23,30)),
         end=tz.localize(datetime(1962, 10, 1, 4, 30)),

         breaks=20, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 17,20)),
         end=tz.localize(datetime(1962, 9, 30, 17, 40)),

         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 6,20)),
         end=tz.localize(datetime(1962, 9, 30, 7, 40)),

         breaks=0, project=running, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 23,30)),
         end=tz.localize(datetime(1962, 4, 1, 4, 30)),

         breaks=20, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 17,20)),
         end=tz.localize(datetime(1962, 3, 31, 17, 40)),
         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 6,20)),
         end=tz.localize(datetime(1962, 3, 31, 7, 40)),
         breaks=0, project=running, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 17,20)),
         end=tz.localize(datetime(1962, 3, 3, 17, 40)),
         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 6,20)),
         end=tz.localize(datetime(1962, 3, 3, 7, 40)),
         breaks=0, project=running, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 12, 3, 17,20)),
         end=tz.localize(datetime(1961, 12, 3, 17, 40)),
         breaks=0, project=archery, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 12, 3, 6,20)),
         end=tz.localize(datetime(1961, 12, 3, 7, 40)),
         breaks=0, project=running, timezone=tz
        )

        # Create things for other user that could clash if not set up properly
        user2 = User.objects.create_user(
         username="john",
         email="jfk@wash.gov",
         password="onassis"
        )
        running2 = Project.objects.create(name="Running", user=user2)
        cycling2 = Project.objects.create(name="Cycling", user=user2)
        health = Project.objects.create(name="Health", user=user2)
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 11, 0)),
         end=tz.localize(datetime(1962, 10, 27, 11, 30)),
         breaks=0, project=running2, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 11,00)),
         end=tz.localize(datetime(1962, 10, 26, 11, 30)),
         breaks=0, project=cycling2, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 11,00)),
         end=tz.localize(datetime(1962, 10, 26, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 11, 0)),
         end=tz.localize(datetime(1962, 9, 30, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 27, 11, 0)),
         end=tz.localize(datetime(1962, 9, 27, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 7, 1, 11,00)),
         end=tz.localize(datetime(1962, 7, 1, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 11,00)),
         end=tz.localize(datetime(1962, 3, 3, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 1, 11,00)),
         end=tz.localize(datetime(1962, 3, 1, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 3, 1, 11,00)),
         end=tz.localize(datetime(1961, 3, 1, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1958, 3, 1, 11,00)),
         end=tz.localize(datetime(1958, 3, 1, 11, 30)),
         breaks=0, project=health, timezone=tz
        )
        self.login()
        self.ultra_id = ultra.id
        self.health_id = health.id
        self.archery_id = archery.id


    @freeze_time("1962-10-27")
    def test_can_view_months(self):
        # The main page shows today's times
        self.get("/")
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")

        # They can view the work done in October
        link = time.find_element_by_class_name("month-link")
        self.click(link)
        self.check_page("/time/1962/10/")
        self.check_title("October 1962")
        self.check_h1("October 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 27)
        for index, day in enumerate(days):
            if index == 0:
                self.check_day_report(day, "4 hours, 30 minutes", [
                 ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
                 ["11:00 - 11:30", "Reading", "30 minutes", None],
                 ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
                 ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
                 ["23:45 - 00:30", "Reading", "45 minutes", None]
                ], date="27 October, 1962")
            elif index == 1:
                self.check_day_report(day, "6 hours", [
                 ["06:20 - 07:40", "Running", "1 hour", None],
                 ["17:20 - 17:40", "Archery", "20 minutes", None],
                 ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="26 October, 1962")
            elif index == 7:
                self.check_day_report(day, "8 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                ], date="20 October, 1962")
            elif index == 11:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="16 October, 1962")
            elif index == 15:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="12 October, 1962")
            elif index == 19:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="8 October, 1962")
            elif index == 24:
                self.check_day_report(day, "6 hours, 20 minutes", [
                 ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                 ["17:20 - 17:40", "Archery", "20 minutes", None],
                 ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="3 October, 1962")
            else:
                self.check_day_report(day, "0 minutes", [])

        # They can view the previous months
        previous = self.browser.find_element_by_id("previous-month")
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("next-month")
        self.click(previous)
        self.check_page("/time/1962/09/")
        self.check_title("September 1962")
        self.check_h1("September 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 30)
        for index, day in enumerate(days):
            if index == 0:
                self.check_day_report(day, "6 hours, 20 minutes", [
                ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                ["17:20 - 17:40", "Archery", "20 minutes", None],
                ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="30 September, 1962")
            else:
                self.check_day_report(day, "0 minutes", [])
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/08/")
        self.check_title("August 1962")
        self.check_h1("August 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        for day in days: self.check_day_report(day, "0 minutes", [])
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/07/")
        self.check_title("July 1962")
        self.check_h1("July 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/06/")
        self.check_title("June 1962")
        self.check_h1("June 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 30)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/05/")
        self.check_title("May 1962")
        self.check_h1("May 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/04/")
        self.check_title("April 1962")
        self.check_h1("April 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 30)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/03/")
        self.check_title("March 1962")
        self.check_h1("March 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        for index, day in enumerate(days):
            if index == 0:
                self.check_day_report(day, "6 hours, 20 minutes", [
                ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                ["17:20 - 17:40", "Archery", "20 minutes", None],
                ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="31 March, 1962")
            elif index == 28:
                self.check_day_report(day, "1 hour, 40 minutes", [
                ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                ["17:20 - 17:40", "Archery", "20 minutes", None],
                ], date="3 March, 1962")
            else:
                self.check_day_report(day, "0 minutes", [])
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/02/")
        self.check_title("February 1962")
        self.check_h1("February 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 28)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1962/01/")
        self.check_title("January 1962")
        self.check_h1("January 1962")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1961/12/")
        self.check_title("December 1961")
        self.check_h1("December 1961")
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 31)
        for index, day in enumerate(days):
            if index == 28:
                self.check_day_report(day, "1 hour, 40 minutes", [
                ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                ["17:20 - 17:40", "Archery", "20 minutes", None],
                ], date="3 December, 1961")
            else:
                self.check_day_report(day, "0 minutes", [])
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("previous-month")
        for n in range(10):
            next = self.browser.find_element_by_id("next-month")
            self.click(next)
        self.check_page("/time/1962/10/")
        self.check_title("October 1962")
        self.check_h1("October 1962")


    def test_month_view_404(self):
        self.logout()
        self.get("/time/1962/10/")
        self.check_page("/")
        self.login()
        self.get("/time/1962/10/")
        self.check_page("/time/1962/10/")
        self.check_h1("October 1962")
        self.get("/time/1952/10/")
        self.check_title("Not Found")


    @freeze_time("1962-10-27")
    def test_can_view_projects(self):
        # User goes to home page
        self.get("/")

        # They decide to look at Project Ultra in more detail
        today = self.browser.find_element_by_class_name("day-time-tracking")
        table = today.find_element_by_tag_name("table")
        for row in table.find_elements_by_tag_name("tr"):
            if "Project Ultra" in row.text:
                link = row.find_element_by_class_name("project-link")
                self.click(link)
                break
        self.check_page("/projects/{}/".format(self.ultra_id))
        self.check_title("Project Ultra")
        self.check_h1("Project Ultra")

        # There are divs for each day of work on the project
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 9)
        self.check_day_report(days[0], "15 minutes", [
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
        ], date="27 October, 1962")
        self.check_day_report(days[1], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="26 October, 1962")
        self.check_day_report(days[2], "8 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
        ], date="20 October, 1962")
        self.check_day_report(days[3], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="16 October, 1962")
        self.check_day_report(days[4], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="12 October, 1962")
        self.check_day_report(days[5], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="8 October, 1962")
        self.check_day_report(days[6], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="3 October, 1962")
        self.check_day_report(days[7], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
         ], date="30 September, 1962")
        self.check_day_report(days[8], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="31 March, 1962")


    def test_project_view_404(self):
        self.logout()
        self.get("/projects/{}/".format(self.ultra_id))
        self.check_page("/")
        self.login()
        self.get("/projects/{}/".format(self.health_id))
        self.check_title("Not Found")
        self.get("/projects/9999999/")
        self.check_title("Not Found")


    def test_can_browse_all_projects(self):
        # User goes to main page
        self.get("/")

        # There is a link to the projects
        time = self.browser.find_element_by_id("time-tracking")
        link = time.find_element_by_class_name("projects-link")
        self.click(link)
        self.check_page("/projects/")
        self.check_title("All Projects")
        self.check_h1("All Projects")

        # The projects are all there
        projects = self.browser.find_elements_by_class_name("project")
        self.assertEqual(len(projects), 5)
        h31 = projects[0].find_element_by_tag_name("h3")
        self.assertEqual(h31.text, "Archery")
        total_time = projects[0].find_element_by_class_name("total-time")
        self.assertIn("2 hours", total_time.text)
        last_done = projects[0].find_element_by_class_name("last-done")
        self.assertIn("26 October, 1962", last_done.text)
        self.click(h31.find_element_by_tag_name("a"))
        self.check_page("/projects/{}/".format(self.archery_id))
        self.browser.back()


    def test_projects_are_out_of_bounds(self):
        self.logout()
        self.get("/projects/")
        self.check_page("/")


    @freeze_time("1962-10-27")
    def test_can_see_other_days(self):
        # The main page shows today's times
        self.get("/")
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")

        # They can view the work done yesterday
        link = time.find_element_by_class_name("yesterday-link")
        self.click(link)
        self.check_page("/time/1962/10/26/")
        self.check_title("26 October, 1962")
        self.check_h1("26 October, 1962")
        day = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(day, "6 hours", [
         ["06:20 - 07:40", "Running", "1 hour", None],
         ["17:20 - 17:40", "Archery", "20 minutes", None],
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="26 October, 1962")

        # There is a form for adding to that day
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        self.assertEqual(start_day_input.get_attribute("value"), "1962-10-26")
        self.assertEqual(end_day_input.get_attribute("value"), "1962-10-26")

        # They can navigate between days
        link = self.browser.find_element_by_class_name("yesterday-link")
        self.click(link)
        self.check_page("/time/1962/10/25/")
        self.check_title("25 October, 1962")
        self.check_h1("25 October, 1962")
        day = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(day, "0 minutes", [], date="25 October, 1962")
        link = self.browser.find_element_by_class_name("tomorrow-link")
        self.click(link)
        self.check_page("/time/1962/10/26/")
        self.check_title("26 October, 1962")
        self.check_h1("26 October, 1962")
        link = self.browser.find_element_by_class_name("tomorrow-link")
        self.click(link)
        self.check_page("/")


    def test_day_view_auth_required(self):
        self.logout()
        self.get("/time/1962/10/26/")
        self.check_page("/")



class SessionEditingTests(TimeTrackingTests):

    def setUp(self):
        FunctionalTest.setUp(self)

        # Create some projects for Sarah
        running = Project.objects.create(name="Running", user=self.user)
        archery = Project.objects.create(name="Archery", user=self.user)
        cooking = Project.objects.create(name="Cooking", user=self.user)
        ultra = Project.objects.create(name="Project Ultra", user=self.user)
        reading = Project.objects.create(name="Reading", user=self.user)

        # Create some sessions for today
        tz = pytz.timezone("Pacific/Auckland")
        timezone.activate(self.user.timezone)
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 11, 0)),
         end=tz.localize(datetime(1962, 10, 27, 11, 30)),
         breaks=0, project=reading, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 12, 0)),
         end=tz.localize(datetime(1962, 10, 27, 12, 15)),
         breaks=0, project=ultra, timezone=tz
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 9, 0)),
         end=tz.localize(datetime(1962, 10, 27, 9, 45)),
         breaks=5, project=cooking, timezone=tz
        )
        session = Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 18, 0)),
         end=tz.localize(datetime(1962, 10, 27, 20, 30)),
         breaks=10, project=reading, timezone=tz
        )
        self.session_id = session.id
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 23, 45)),
         end=tz.localize(datetime(1962, 10, 28, 0, 30)),
         breaks=0, project=reading, timezone=tz
        )

        # Create sessions from other user
        user2 = User.objects.create_user(
         username="john",
         email="jfk@wash.gov",
         password="onassis"
        )
        running2 = Project.objects.create(name="Running", user=user2)
        other = Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 11, 0)),
         end=tz.localize(datetime(1962, 10, 27, 11, 30)),
         breaks=0, project=running2, timezone=tz
        )
        self.other_id = other.id
        self.login()


    @freeze_time("1962-10-27")
    def test_can_edit_session_to_new_project(self):
        # The user goes to the home page
        self.get("/")
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")

        # They go to edit the excessive reading
        row = today.find_elements_by_tag_name("tr")[3]
        self.assertIn("2 hours, 20 minutes", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # The form has pre-loaded values
        self.check_session_form(
         start_day="1962-10-27", end_day="1962-10-27",
         start_time="18:00", end_time="20:30", breaks="10", project="Reading"
        )

        # They change those values and submit
        self.fill_in_session_form(
         "23:00", "02:00", "30", "Base Jumping",
         start_day="1962-10-15", end_day="1962-10-16"
        )

        # They are on the October page
        self.check_page("/time/1962/10/15/")

        # The sessions are updated
        day = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(day, "2 hours, 30 minutes", [
         ["23:00 - 02:00", "Base Jumping", "2 hours, 30 minutes", "30 minutes"],
        ], date="15 October, 1962")


    @freeze_time("1962-10-27")
    def test_can_edit_session_to_existing_project(self):
        # The user goes to the home page
        self.get("/")
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")

        # They go to edit the excessive reading
        row = today.find_elements_by_tag_name("tr")[3]
        self.assertIn("2 hours, 20 minutes", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # The form has pre-loaded values
        self.check_session_form(
         start_day="1962-10-27", end_day="1962-10-27",
         start_time="18:00", end_time="20:30", breaks="10", project="Reading"
        )

        # They change those values and submit
        self.fill_in_session_form(
         "23:00", "02:00", "30", "Project Ultra", existing=True,
         start_day="1961-04-15", end_day="1961-04-16"
        )

        # They are on the October page
        self.check_page("/time/1961/04/15/")

        # The sessions are updated
        day = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(day, "2 hours, 30 minutes", [
         ["23:00 - 02:00", "Project Ultra", "2 hours, 30 minutes", "30 minutes"],
        ], date="15 April, 1961")


    def test_session_editing_view_404(self):
        self.logout()
        self.get("/sessions/{}/".format(self.session_id))
        self.check_page("/")
        self.login()
        self.get("/sessions/{}/".format(self.other_id))
        self.check_title("Not Found")
        self.get("/sessions/9999999/")
        self.check_title("Not Found")


    @freeze_time("1962-10-27")
    def test_can_delete_session(self):
        # The user goes to the home page
        self.get("/")
        time = self.browser.find_element_by_id("time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")

        # They go to edit the excessive reading
        row = today.find_elements_by_tag_name("tr")[3]
        self.assertIn("2 hours, 20 minutes", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # There is a link to the deletion page
        link = self.browser.find_element_by_class_name("delete-link")
        self.click(link)
        self.check_page("/sessions/{}/delete/".format(self.session_id))
        self.check_title("Delete Session")
        self.check_h1("Delete Session")

        # They can go back
        main = self.browser.find_element_by_tag_name("main")
        self.assertIn("are you sure", main.text.lower())
        self.assertIn("Reading", main.text)
        self.assertIn("2 hours, 20 minutes", main.text)
        back_link = main.find_element_by_class_name("back-link")
        self.click(back_link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # But they want to delete
        link = self.browser.find_element_by_class_name("delete-link")
        self.click(link)
        self.check_page("/sessions/{}/delete/".format(self.session_id))
        self.check_title("Delete Session")
        self.check_h1("Delete Session")
        delete = self.browser.find_element_by_class_name("delete-button")
        self.click(delete)
        self.check_page("/time/1962/10/27/")
        day = self.browser.find_element_by_class_name("day-time-tracking")
        self.check_day_report(day, "2 hours, 10 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27 October, 1962")


    def test_session_deletion_view_404(self):
        self.logout()
        self.get("/sessions/{}/delete/".format(self.session_id))
        self.check_page("/")
        self.login()
        self.get("/sessions/{}/delete/".format(self.other_id))
        self.check_title("Not Found")
        self.get("/sessions/9999999/delete/")
        self.check_title("Not Found")
