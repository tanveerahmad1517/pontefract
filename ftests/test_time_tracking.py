from datetime import datetime, date
import pytz
from selenium.webdriver.common.keys import Keys
from django.utils import timezone
from projects.models import Project, Session
from core.models import User
from freezegun import freeze_time
from .base import FunctionalTest

class TimeTrackingTests(FunctionalTest):

    def fill_in_session_form(self, now, start_time, end_time, breaks, project, existing=False):
        # There is a form to record work
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]

        # The form default values are sensible
        self.assertEqual(start_day_input.get_attribute("type"), "date")
        self.assertEqual(start_time_input.get_attribute("type"), "time")
        self.assertEqual(end_day_input.get_attribute("type"), "date")
        self.assertEqual(end_time_input.get_attribute("type"), "time")
        self.assertEqual(start_day_input.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(end_day_input.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(breaks_input.get_attribute("value"), "0")

        # They enter some values and submit
        start_time_input.send_keys(start_time)
        end_time_input.send_keys(end_time)
        breaks_input.clear()
        if breaks != "0": breaks_input.send_keys(breaks)
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


    def check_day_report(self, div, total, sessions, date=None):
        if date:
            self.assertEqual(div.find_element_by_tag_name("h3").text, date)
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
        now = timezone.localtime(timezone.now())

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0635AM", "10", "Dog Walking"
        )

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "20 minutes", [
         ["06:05 - 06:35", "Dog Walking", "20 minutes", "10 minute break"]
        ])


    def test_can_add_work_session_to_existing_project(self):
        Project.objects.create(name="Running", user=self.user)
        Project.objects.create(name="Cycling", user=self.user)
        Project.objects.create(name="Swimming", user=self.user)

        # The user goes to the home page and fills out the form there
        self.login()
        self.get("/")
        now = timezone.localtime(timezone.now())
        self.fill_in_session_form(
         now, "1605PM", "1635PM", "0", "Cycling", existing=True
        )

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "30 minutes", [
         ["16:05 - 16:35", "Cycling", "30 minutes", None]
        ])


    def test_second_time_must_be_after_first(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = timezone.localtime(timezone.now())

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0505AM", "10", "Dog Walking"
        )

        # They are still on the home page and there are no sessions
        self.check_page("/")
        self.assertEqual(self.browser.find_elements_by_class_name("session"), [])

        # There is an error message and the form is still filled in
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(start_time_input.get_attribute("value"), "06:05")
        self.assertEqual(end_time_input.get_attribute("value"), "05:05")
        error = form.find_element_by_id("end-error")
        self.assertIn("before", error.text)


    def test_breaks_must_be_positive(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = timezone.localtime(timezone.now())

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0705AM", "-10", "Dog Walking"
        )

        # They are still on the home page and there are no sessions
        self.check_page("/")
        self.assertEqual(self.browser.find_elements_by_class_name("session"), [])

        # There is an error message and the form is still filled in
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(start_time_input.get_attribute("value"), "06:05")
        self.assertEqual(end_time_input.get_attribute("value"), "07:05")
        error = form.find_element_by_id("breaks-error")
        self.assertIn("positive", error.text)


    def test_breaks_must_not_cancel_out_session(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = timezone.localtime(timezone.now())

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0705AM", "70", "Dog Walking"
        )

        # They are still on the home page and there are no sessions
        self.check_page("/")
        self.assertEqual(self.browser.find_elements_by_class_name("session"), [])

        # There is an error message and the form is still filled in
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(start_time_input.get_attribute("value"), "06:05")
        self.assertEqual(end_time_input.get_attribute("value"), "07:05")
        error = form.find_element_by_id("breaks-error")
        self.assertIn("cancel", error.text)


    def test_project_name_cannot_be_spaces(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = timezone.localtime(timezone.now())

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0705AM", "70", "   "
        )

        # They are still on the home page and there are no sessions
        self.check_page("/")
        self.assertEqual(self.browser.find_elements_by_class_name("session"), [])

        # There is an error message and the form is still filled in
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        self.assertEqual(start_time_input.get_attribute("value"), "06:05")
        self.assertEqual(end_time_input.get_attribute("value"), "07:05")
        error = form.find_element_by_id("project-error")
        self.assertIn("valid", error.text)



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
         breaks=0, project=reading
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 12, 0)),
         end=tz.localize(datetime(1962, 10, 27, 12, 15)),
         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 9, 0)),
         end=tz.localize(datetime(1962, 10, 27, 9, 45)),
         breaks=5, project=cooking
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 18, 0)),
         end=tz.localize(datetime(1962, 10, 27, 20, 30)),
         breaks=10, project=reading
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 23, 45)),
         end=tz.localize(datetime(1962, 10, 28, 0, 30)),
         breaks=0, project=reading
        )

        # Create sessions for current month
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 23, 30)),
         end=tz.localize(datetime(1962, 10, 27, 4, 30)),

         breaks=20, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 17,20)),
         end=tz.localize(datetime(1962, 10, 26, 17, 40)),

         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 6,20)),
         end=tz.localize(datetime(1962, 10, 26, 7, 40)),

         breaks=0, project=running
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 20, 9,00)),
         end=tz.localize(datetime(1962, 10, 20, 17, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 16, 9,00)),
         end=tz.localize(datetime(1962, 10, 16, 17, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 16, 18,00)),
         end=tz.localize(datetime(1962, 10, 16, 22, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 12, 9,00)),
         end=tz.localize(datetime(1962, 10, 12, 17, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 12, 18,00)),
         end=tz.localize(datetime(1962, 10, 12, 22, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 8, 9,00)),
         end=tz.localize(datetime(1962, 10, 8, 17, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 8, 18,00)),
         end=tz.localize(datetime(1962, 10, 8, 22, 00)),

         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 23,30)),
         end=tz.localize(datetime(1962, 10, 4, 4, 30)),

         breaks=20, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 17,20)),
         end=tz.localize(datetime(1962, 10, 3, 17, 40)),

         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 6,20)),
         end=tz.localize(datetime(1962, 10, 3, 7, 40)),

         breaks=0, project=running
        )

        # Create sessions for previous months
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 23,30)),
         end=tz.localize(datetime(1962, 10, 1, 4, 30)),

         breaks=20, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 17,20)),
         end=tz.localize(datetime(1962, 9, 30, 17, 40)),

         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 6,20)),
         end=tz.localize(datetime(1962, 9, 30, 7, 40)),

         breaks=0, project=running
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 23,30)),
         end=tz.localize(datetime(1962, 4, 1, 4, 30)),

         breaks=20, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 17,20)),
         end=tz.localize(datetime(1962, 3, 31, 17, 40)),
         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 31, 6,20)),
         end=tz.localize(datetime(1962, 3, 31, 7, 40)),
         breaks=0, project=running
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 17,20)),
         end=tz.localize(datetime(1962, 3, 3, 17, 40)),
         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 6,20)),
         end=tz.localize(datetime(1962, 3, 3, 7, 40)),
         breaks=0, project=running
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 12, 3, 17,20)),
         end=tz.localize(datetime(1961, 12, 3, 17, 40)),
         breaks=0, project=archery
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 12, 3, 6,20)),
         end=tz.localize(datetime(1961, 12, 3, 7, 40)),
         breaks=0, project=running
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
         breaks=0, project=running2
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 26, 11,00)),
         end=tz.localize(datetime(1962, 10, 26, 11, 30)),
         breaks=0, project=cycling2
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 3, 11,00)),
         end=tz.localize(datetime(1962, 10, 26, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 30, 11, 0)),
         end=tz.localize(datetime(1962, 9, 30, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 9, 27, 11, 0)),
         end=tz.localize(datetime(1962, 9, 27, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 7, 1, 11,00)),
         end=tz.localize(datetime(1962, 7, 1, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 3, 11,00)),
         end=tz.localize(datetime(1962, 3, 3, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 3, 1, 11,00)),
         end=tz.localize(datetime(1962, 3, 1, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1961, 3, 1, 11,00)),
         end=tz.localize(datetime(1961, 3, 1, 11, 30)),
         breaks=0, project=health
        )
        Session.objects.create(
         start=tz.localize(datetime(1958, 3, 1, 11,00)),
         end=tz.localize(datetime(1958, 3, 1, 11, 30)),
         breaks=0, project=health
        )
        self.login()
        self.ultra_id = ultra.id
        self.health_id = health.id
        self.archery_id = archery.id


    @freeze_time("1962-10-27")
    def test_can_view_months(self):
        # The main page shows today's times
        self.get("/")
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27th October 1962")

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
                ], date="27th October 1962")
            elif index == 1:
                self.check_day_report(day, "6 hours", [
                 ["06:20 - 07:40", "Running", "1 hour", None],
                 ["17:20 - 17:40", "Archery", "20 minutes", None],
                 ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="26th October 1962")
            elif index == 7:
                self.check_day_report(day, "8 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                ], date="20th October 1962")
            elif index == 11:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="16th October 1962")
            elif index == 15:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="12th October 1962")
            elif index == 19:
                self.check_day_report(day, "12 hours", [
                 ["09:00 - 17:00", "Project Ultra", "8 hours", None],
                 ["18:00 - 22:00", "Project Ultra", "4 hours", None],
                ], date="8th October 1962")
            elif index == 24:
                self.check_day_report(day, "6 hours, 20 minutes", [
                 ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                 ["17:20 - 17:40", "Archery", "20 minutes", None],
                 ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
                ], date="3rd October 1962")
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
                ], date="30th September 1962")
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
                ], date="31st March 1962")
            elif index == 28:
                self.check_day_report(day, "1 hour, 40 minutes", [
                ["06:20 - 07:40", "Running", "1 hour, 20 minutes", None],
                ["17:20 - 17:40", "Archery", "20 minutes", None],
                ], date="3rd March 1962")
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
                ], date="3rd December 1961")
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
        ], date="27th October 1962")
        self.check_day_report(days[1], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="26th October 1962")
        self.check_day_report(days[2], "8 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
        ], date="20th October 1962")
        self.check_day_report(days[3], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="16th October 1962")
        self.check_day_report(days[4], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="12th October 1962")
        self.check_day_report(days[5], "12 hours", [
         ["09:00 - 17:00", "Project Ultra", "8 hours", None],
         ["18:00 - 22:00", "Project Ultra", "4 hours", None],
        ], date="8th October 1962")
        self.check_day_report(days[6], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="3rd October 1962")
        self.check_day_report(days[7], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
         ], date="30th September 1962")
        self.check_day_report(days[8], "4 hours, 40 minutes", [
         ["23:30 - 04:30", "Project Ultra", "4 hours, 40 minutes", "20 minutes"],
        ], date="31st March 1962")


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
        time = self.browser.find_element_by_id("user-time-tracking")
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
        self.assertIn("26th October 1962", last_done.text)
        self.click(h31.find_element_by_tag_name("a"))
        self.check_page("/projects/{}/".format(self.archery_id))
        self.browser.back()


    def test_projects_are_out_of_bounds(self):
        self.logout()
        self.get("/projects/")
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
         breaks=0, project=reading
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 12, 0)),
         end=tz.localize(datetime(1962, 10, 27, 12, 15)),
         breaks=0, project=ultra
        )
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 9, 0)),
         end=tz.localize(datetime(1962, 10, 27, 9, 45)),
         breaks=5, project=cooking
        )
        session = Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 18, 0)),
         end=tz.localize(datetime(1962, 10, 27, 20, 30)),
         breaks=10, project=reading
        )
        self.session_id = session.id
        Session.objects.create(
         start=tz.localize(datetime(1962, 10, 27, 23, 45)),
         end=tz.localize(datetime(1962, 10, 28, 0, 30)),
         breaks=0, project=reading
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
         breaks=0, project=running2
        )
        self.other_id = other.id
        self.login()


    @freeze_time("1962-10-27")
    def test_can_edit_session_to_new_project(self):
        # The user goes to the home page
        self.get("/")
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27th October 1962")

        # They go to edit the excessive reading
        row = today.find_elements_by_tag_name("tr")[3]
        self.assertIn("2 hours, 20 minutes", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # There is a form
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]

        # The form has pre-loaded values
        self.assertEqual(start_day_input.get_attribute("value"), "1962-10-27")
        self.assertEqual(start_time_input.get_attribute("value"), "18:00")
        self.assertEqual(end_day_input.get_attribute("value"), "1962-10-27")
        self.assertEqual(end_time_input.get_attribute("value"), "20:30")
        self.assertEqual(breaks_input.get_attribute("value"), "10")
        self.assertEqual(project_input.get_attribute("value"), "Reading")

        # They change those values and submit
        start_day_input.send_keys(Keys.DELETE)
        start_day_input.send_keys("15101962")
        start_time_input.send_keys(Keys.DELETE)
        start_time_input.send_keys("23:00")
        end_day_input.send_keys(Keys.DELETE)
        end_day_input.send_keys("16101962")
        end_time_input.send_keys(Keys.DELETE)
        end_time_input.send_keys("02:00")
        breaks_input.clear()
        breaks_input.send_keys(30)
        project_input.clear()
        project_input.send_keys("Base Jumping")
        self.click(form.find_elements_by_tag_name("input")[-1])

        # They are on the October page
        self.check_page("/time/1962/10/")

        # The sessions are updated
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 27)
        self.check_day_report(days[0], "2 hours, 10 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27th October 1962")
        self.check_day_report(days[12], "2 hours, 30 minutes", [
         ["23:00 - 02:00", "Base Jumping", "2 hours, 30 minutes", "30 minutes"],
        ], date="15th October 1962")


    @freeze_time("1962-10-27")
    def test_can_edit_session_to_existing_project(self):
        # The user goes to the home page
        self.get("/")
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_class_name("day-time-tracking")
        self.check_day_report(today, "4 hours, 30 minutes", [
         ["09:00 - 09:45", "Cooking", "40 minutes", "5 minutes"],
         ["11:00 - 11:30", "Reading", "30 minutes", None],
         ["12:00 - 12:15", "Project Ultra", "15 minutes", None],
         ["18:00 - 20:30", "Reading", "2 hours, 20 minutes", "10 minutes"],
         ["23:45 - 00:30", "Reading", "45 minutes", None]
        ], date="27th October 1962")

        # They go to edit the excessive reading
        row = today.find_elements_by_tag_name("tr")[3]
        self.assertIn("2 hours, 20 minutes", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/".format(self.session_id))
        self.check_title("Edit Session")
        self.check_h1("Edit Session")

        # There is a form
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]

        # The form has pre-loaded values
        self.assertEqual(start_day_input.get_attribute("value"), "1962-10-27")
        self.assertEqual(start_time_input.get_attribute("value"), "18:00")
        self.assertEqual(end_day_input.get_attribute("value"), "1962-10-27")
        self.assertEqual(end_time_input.get_attribute("value"), "20:30")
        self.assertEqual(breaks_input.get_attribute("value"), "10")
        self.assertEqual(project_input.get_attribute("value"), "Reading")

        # They change those values and submit
        start_day_input.send_keys(Keys.DELETE)
        start_day_input.send_keys("15041961")
        start_time_input.send_keys(Keys.DELETE)
        start_time_input.send_keys("23:00")
        end_day_input.send_keys(Keys.DELETE)
        end_day_input.send_keys("16041961")
        end_time_input.send_keys(Keys.DELETE)
        end_time_input.send_keys("02:00")
        breaks_input.clear()
        breaks_input.send_keys(30)
        project_input.clear()
        project_input.send_keys("Project Ultra")
        self.click(form.find_elements_by_tag_name("input")[-1])

        # They are on the October page
        self.check_page("/time/1961/04/")

        # The sessions are updated
        days = self.browser.find_elements_by_class_name("day-time-tracking")
        self.assertEqual(len(days), 30)
        self.check_day_report(days[15], "2 hours, 30 minutes", [
         ["23:00 - 02:00", "Project Ultra", "2 hours, 30 minutes", "30 minutes"],
        ], date="15th April 1961")


    def test_session_editing_view_404(self):
        self.logout()
        self.get("/sessions/{}/".format(self.session_id))
        self.check_page("/")
        self.login()
        self.get("/sessions/{}/".format(self.other_id))
        self.check_title("Not Found")
        self.get("/sessions/9999999/")
        self.check_title("Not Found")
