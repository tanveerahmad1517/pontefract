from datetime import datetime, date
import pytz
from selenium.webdriver.common.keys import Keys
from django.utils import timezone
from projects.models import Project, Session
from core.models import User
from freezegun import freeze_time
from .base import FunctionalTest

class TimeTrackingTest(FunctionalTest):

    def fill_in_session_form(self, start_time, end_time, breaks,
     project, notes=None, existing=False, start_day=None, end_day=None):
        # There is a form to record work
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        notes_input = form.find_element_by_tag_name("textarea")
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
        if notes:
            notes_input.send_keys(notes)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)


    def check_session_form(self, start_day=None, start_time=None, end_day=None,
     end_time=None, breaks=None, project=None, notes=None, start_error=None,
     end_error=None, breaks_error=None, project_error=None):
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        notes_input = form.find_element_by_tag_name("textarea")
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
        if notes:
            self.assertEqual(notes_input.get_attribute("value"), notes)
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
        self.assertEqual(len(sessions), len(session_divs) if sessions else len(session_divs) - 1)
        for session, session_div in zip(sessions, session_divs):
            cells = session_div.find_elements_by_class_name("cell")
            self.assertIn(session[0], cells[0].text)
            self.assertIn(session[1], cells[2].text)
            self.assertIn(session[2], cells[3].text)
            if session[3]:
                self.assertIn(session[3], cells[4].text)
            else:
                self.assertEqual(cells[4].text, "-")
            if len(session) > 4:
                button = session_div.find_element_by_tag_name("button")
                open_notes = div.find_elements_by_tag_name("span")
                button.click()
                new_open_notes = div.find_elements_by_tag_name("span")
                self.assertEqual(
                 len(open_notes) + 1, len(new_open_notes)
                )
                notes = [n for n in new_open_notes if n not in open_notes][0]
                self.assertEqual(notes.text, session[4])
                button.click()
                self.sleep(0.6)
                new_open_notes = div.find_elements_by_tag_name("span")
                self.assertEqual(
                 len(open_notes), len(new_open_notes)
                )


    def fill_in_project_form(self, name):
        form = self.browser.find_elements_by_tag_name("form")[1]
        name_input = form.find_elements_by_tag_name("input")[0]
        name_input.clear()
        name_input.send_keys(name)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)


    def check_project_form(self, name=None, name_error=None):
        form = self.browser.find_elements_by_tag_name("form")[1]
        name_input = form.find_elements_by_tag_name("input")[0]
        if name:
            self.assertEqual(name_input.get_attribute("value"), name)
        if name_error:
            error = form.find_element_by_id("name-error")
            self.assertIn(name_error, error.text)



class SessionAddingTests(TimeTrackingTest):

    def test_can_add_work_session(self):
        # User goes to the home page
        self.login()
        self.get("/")

        # There are two sessions already there
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
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
        self.fill_in_session_form(
         "16:05", "16:35", "0", "Cycling", existing=True, notes="Some notes."
        )

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 50 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None],
         ["16:05 - 16:35", "Cycling", "30 minutes", None, "Some notes."]
        ])


    def test_can_add_work_session_for_previous_day(self):
        # The user goes to the yesetrday page and fills out the form there
        self.login()
        self.get("/day/2009-10-01/")
        self.fill_in_session_form("16:05", "16:35", "0", "Cycling")

        # They are on the day's page
        self.check_page("/day/2009-10-01/")

        # The total for the day is updated
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
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
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # There is an error message and the form is still filled in
        self.check_session_form(
         start_time="06:05", end_time="07:05", breaks="10", project_error="valid"
        )



class ProjectAddingTests(TimeTrackingTest):

    def test_can_add_new_project(self):
        # User goes to projects page
        self.login()
        self.get("/")
        self.click(self.browser.find_element_by_id("projects-link"))
        self.check_page("/projects/")

        # There is a link to add a new project
        title = self.browser.find_element_by_class_name("title-box")
        link = title.find_element_by_tag_name("a")
        self.assertIn("new project", link.text.lower())
        self.click(link)
        self.check_page("/projects/new/")
        self.check_title("New Project")

        # There is a form
        form = self.browser.find_elements_by_tag_name("form")[1]
        name_input = form.find_elements_by_tag_name("input")[0]

        # They enter some data
        name_input.send_keys("Project Ultra")
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)

        # They are on the project page
        self.check_page(
         "/projects/{}/".format(Project.objects.get(name="Project Ultra").id)
        )
        title_div = self.browser.find_element_by_class_name("title-box")
        self.assertEqual(
         title_div.find_element_by_tag_name("h1").text, "Project Ultra"
        )
        self.assertEqual(
         title_div.find_element_by_class_name("total-time").text, "0 minutes"
        )
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 0)



    def test_need_to_be_logged_in_to_make_new_project(self):
        self.get("/projects/new/")
        self.check_page("/")


    def test_project_name_must_be_valid(self):
        # User goes to the new project page
        self.login()
        self.get("/projects/new/")

        # They fill out the project form that is there
        self.fill_in_project_form("    ")

        # They are still on the new projects page
        self.check_page("/projects/new/")

        # There is an error message and the form is still filled in
        self.check_project_form(
         name="", name_error="valid"
        )



class SessionViewingTests(TimeTrackingTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.login()


    def test_can_see_other_days(self):
        # The main page shows today's times
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They can view the work done yesterday
        link = self.browser.find_element_by_class_name("yesterday-link")
        self.click(link)
        self.check_page("/day/1997-05-01/")
        self.check_title("1 May, 1997")
        day = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(day, "1 hour, 20 minutes", [
         ["15:30 - 16:10", "Research", "40 minutes", None],
         ["23:30 - 00:10", "Research", "40 minutes", ""],
        ])

        # There is a form for adding to that day
        form = self.browser.find_elements_by_tag_name("form")[1]
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        project_input = form.find_elements_by_tag_name("input")[5]
        self.assertEqual(start_day_input.get_attribute("value"), "1997-05-01")
        self.assertEqual(end_day_input.get_attribute("value"), "1997-05-01")

        # They can navigate between days
        link = self.browser.find_element_by_class_name("yesterday-link")
        self.click(link)
        self.check_page("/day/1997-04-30/")
        self.check_title("30 April, 1997")
        day = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(day, "0 minutes", [], date="30 April, 1997")
        self.assertIn("no sessions", day.text)
        link = day.find_element_by_class_name("tomorrow-link")
        self.click(link)
        self.check_page("/day/1997-05-01/")
        self.check_title("1 May, 1997")
        link = self.browser.find_element_by_class_name("tomorrow-link")
        self.click(link)
        self.check_page("/")


    def test_day_view_auth_required(self):
        self.logout()
        self.get("/day/1997-05-01/")
        self.check_page("/")


    def test_can_view_months(self):
        # The main page shows today's times
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They can view the work done in May
        link = today.find_element_by_class_name("month-link")
        self.click(link)
        self.check_page("/time/1997-05/")
        self.check_title("May 1997")
        self.check_h1("May 1997")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 2)
        self.check_day_report(days[0], "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ], date="2 May, 1997")
        self.check_day_report(days[1], "1 hour, 20 minutes", [
         ["15:30 - 16:10", "Research", "40 minutes", None],
         ["23:30 - 00:10", "Research", "40 minutes", ""],
        ], date="1 May, 1997")

        # They can view the previous months
        previous = self.browser.find_element_by_id("previous-month")
        with self.assertRaises(self.NoElement):
            self.browser.find_element_by_id("next-month")
        self.click(previous)
        self.check_page("/time/1997-04/")
        self.check_title("April 1997")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 30)
        for index, day in enumerate(days):
            if index == 9:
                self.check_day_report(day, "1 hour, 15 minutes", [
                ["15:20 - 16:00", "Teaching", "35 minutes", "5 minute"],
                ["20:05 - 21:00", "Coding", "40 minutes", "15 minute"],
                ], date="21 April, 1997")
            elif index == 28:
                self.check_day_report(day, "10 minutes", [
                ["12:00 - 12:10", "Fencing", "10 minutes", ""],
                ], date="2 April, 1997")
            else:
                self.check_day_report(day, "0 minutes", [])
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1997-03/")
        self.check_title("March 1997")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 31)
        for day in days: self.check_day_report(day, "0 minutes", [])
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1997-02/")
        self.check_title("February 1997")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 28)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1997-01/")
        self.check_title("January 1997")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 31)
        previous = self.browser.find_element_by_id("previous-month")
        self.click(previous)
        self.check_page("/time/1996-12/")
        self.check_title("December 1996")
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 31)
        for index, day in enumerate(days):
            if index == 7:
                self.check_day_report(day, "2 hours, 35 minutes", [
                ["12:00 - 12:10", "Gym", "10 minutes", ""],
                ["15:20 - 16:00", "Cycling", "35 minutes", "5 minute"],
                ["19:00 - 20:10", "Research", "1 hour, 10 minutes", None],
                ["20:05 - 21:00", "Running", "40 minutes", "15 minute"],
                ], date="24 December, 1996")
            else:
                self.check_day_report(day, "0 minutes", [])
        for n in range(5):
            next = self.browser.find_element_by_id("next-month")
            self.click(next)
        self.check_page("/time/1997-05/")
        self.check_title("May 1997")


    def test_month_view_404(self):
        self.logout()
        self.get("/time/1997-05/")
        self.check_page("/")
        self.login()
        self.get("/time/1997-05/")
        self.check_page("/time/1997-05/")
        self.check_title("May 1997")


    def test_can_view_project(self):
        # User goes to home page
        self.get("/")

        # They decide to look at Research in more detail
        today = self.browser.find_element_by_class_name("day-sessions")
        table = today.find_element_by_class_name("sessions")
        for row in table.find_elements_by_class_name("session"):
            if "Research" in row.text:
                link = row.find_element_by_class_name("project-link")
                self.click(link)
                break
        self.check_page("/projects/{}/".format(self.research.id))
        self.check_title("Research")
        self.check_h1("Research")

        # There is information at the top
        title_div = self.browser.find_element_by_class_name("title-box")
        self.assertEqual(
         title_div.find_element_by_tag_name("h1").text, "Research"
        )
        self.assertEqual(
         title_div.find_element_by_class_name("total-time").text, "2 hours, 50 minutes"
        )

        # There are divs for each day of work on the project
        days = self.browser.find_elements_by_class_name("day-sessions")
        self.assertEqual(len(days), 3)
        self.check_day_report(days[0], "20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
        ], date="2 May, 1997")
        self.check_day_report(days[1], "1 hour, 20 minutes", [
         ["15:30 - 16:10", "Research", "40 minutes", None],
         ["23:30 - 00:10", "Research", "40 minutes", None],
        ], date="1 May, 1997")
        self.check_day_report(days[2], "1 hour, 10 minutes", [
         ["19:00 - 20:10", "Research", "1 hour, 10 minutes", None],
        ], date="24 December, 1996")


    def test_project_view_404(self):
        self.logout()
        self.get("/projects/{}/".format(self.research.id))
        self.check_page("/")
        self.login()
        self.get("/projects/{}/".format(self.running2.id))
        self.check_title("Not Found")
        self.get("/projects/9999999/")
        self.check_title("Not Found")


    def test_can_browse_all_projects(self):
        # User goes to main page
        self.get("/")

        # There is a link to the projects
        nav = self.browser.find_element_by_tag_name("nav")
        link = nav.find_element_by_id("projects-link")
        self.click(link)
        self.check_page("/projects/")
        self.check_title("All Projects")

        # The projects are all there
        projects = self.browser.find_elements_by_class_name("project")
        self.assertEqual(len(projects), 8)
        self.assertEqual(
         projects[0].find_element_by_class_name("project-name").text, "Research"
        )
        self.assertIn(
         "2 hours, 50 minutes", projects[0].find_element_by_class_name("total-time").text
        )
        self.assertIn(
         "today", projects[0].find_element_by_class_name("last-done").text
        )
        self.assertEqual(
         projects[-1].find_element_by_class_name("project-name").text, "Fencing"
        )
        self.assertIn(
         "10 minutes", projects[-1].find_element_by_class_name("total-time").text
        )
        self.assertIn(
         "2 April", projects[-1].find_element_by_class_name("last-done").text
        )
        self.click(projects[-1].find_element_by_class_name("project-name"))
        self.check_page("/projects/{}/".format(self.fencing.id))


    def test_projects_are_out_of_bounds(self):
        self.logout()
        self.get("/projects/")
        self.check_page("/")



class SessionEditingTests(TimeTrackingTest):

    def setUp(self):
        FunctionalTest.setUp(self)
        self.session_id = Project.objects.get(name="Yoga").session_set.get(start__day=2).id
        self.other_id = Session.objects.last().id
        self.login()


    def test_can_edit_session_to_new_project(self):
        # The user goes to the home page
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They go to edit the Yoga
        row = today.find_elements_by_class_name("session")[1]
        self.assertIn("1 hour", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/edit/".format(self.session_id))
        self.check_title("Edit Session")

        # The form has pre-loaded values
        self.check_session_form(
         start_day="1997-05-02", end_day="1997-05-02", notes="",
         start_time="01:00", end_time="02:00", breaks="", project="Yoga"
        )

        # They change those values and submit
        self.fill_in_session_form(
         "23:45", "03:00", "10", "Base Jumping", notes="new note",
         start_day="1996-05-01", end_day="1996-05-02"
        )

        # They are on the October page
        self.check_page("/day/1996-05-01/")

        # The sessions are updated
        day = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(day, "3 hours, 5 minutes", [
         ["23:45 - 03:00", "Base Jumping", "3 hours, 5 minutes", "10 minute", "new note"],
        ], date="1 May, 1996")


    def test_can_edit_session_to_existing_project(self):
        # The user goes to the home page
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They go to edit the Yoga
        row = today.find_elements_by_class_name("session")[1]
        self.assertIn("1 hour", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/edit/".format(self.session_id))
        self.check_title("Edit Session")

        # The form has pre-loaded values
        self.check_session_form(
         start_day="1997-05-02", end_day="1997-05-02",
         start_time="01:00", end_time="02:00", breaks="", project="Yoga"
        )

        # They change those values and submit
        self.fill_in_session_form(
         "23:45", "03:00", "10", "Base Jumping",
         start_day="1996-05-01", end_day="1996-05-02"
        )

        # They are on the October page
        self.check_page("/day/1996-05-01/")

        # The sessions are updated
        day = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(day, "3 hours, 5 minutes", [
         ["23:45 - 03:00", "Base Jumping", "3 hours, 5 minutes", "10 minute"],
        ], date="1 May, 1996")


    def test_session_editing_view_404(self):
        self.logout()
        self.get("/sessions/{}/edit/".format(self.session_id))
        self.check_page("/")
        self.login()
        self.get("/sessions/{}/edit/".format(self.other_id))
        self.check_title("Not Found")
        self.get("/sessions/9999999/edit/")
        self.check_title("Not Found")


    def test_can_delete_session(self):
        # The user goes to the home page
        self.get("/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "1 hour, 20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
         ["01:00 - 02:00", "Yoga", "1 hour", None]
        ])

        # They go to edit the yoga
        row = today.find_elements_by_class_name("session")[1]
        self.assertIn("1 hour", row.text)
        link = row.find_element_by_class_name("edit-link")
        self.click(link)
        self.check_page("/sessions/{}/edit/".format(self.session_id))
        self.check_title("Edit Session")

        # There is a link to the deletion page
        link = self.browser.find_element_by_class_name("delete-button")
        self.click(link)
        self.check_page("/sessions/{}/delete/".format(self.session_id))
        self.check_title("Delete Session")

        # They can go back
        main = self.browser.find_element_by_tag_name("main")
        self.assertIn("are you sure", main.text.lower())
        self.assertIn("Yoga", main.text)
        self.assertIn("1 hour", main.text)
        back_link = main.find_element_by_id("back-link")
        self.click(back_link)
        self.check_page("/sessions/{}/edit/".format(self.session_id))
        self.check_title("Edit Session")

        # But they want to delete
        link = self.browser.find_element_by_class_name("delete-button")
        self.click(link)
        self.check_page("/sessions/{}/delete/".format(self.session_id))
        self.check_title("Delete Session")
        delete = self.browser.find_element_by_class_name("delete-button")
        self.click(delete)
        self.check_page("/day/1997-05-02/")
        today = self.browser.find_element_by_class_name("day-sessions")
        self.check_day_report(today, "20 minutes", [
         ["00:30 - 00:55", "Research", "20 minutes", "5 minute break"],
        ])


    def test_session_deletion_view_404(self):
        self.logout()
        self.get("/sessions/{}/delete/".format(self.session_id))
        self.check_page("/")
        self.login()
        self.get("/sessions/{}/delete/".format(self.other_id))
        self.check_title("Not Found")
        self.get("/sessions/9999999/delete/")
        self.check_title("Not Found")



class ProjectEditingTests(TimeTrackingTest):

    def test_can_edit_project(self):
        # User goes to project page
        self.login()
        self.get("/projects/")
        first_project = self.browser.find_elements_by_class_name("project")[0]
        self.click(first_project.find_element_by_tag_name("a"))

        # There is a link to edit the project
        edit_link = self.browser.find_element_by_class_name("edit-link")
        self.click(edit_link)
        self.check_page("/projects/{}/edit/".format(self.research.id))
        self.check_title("Edit Project")

        # There is a form, which they modify
        self.check_project_form(name="Research")
        self.fill_in_project_form(name="Super Research")

        # They are back on the project page and the project is changed
        self.check_page("/projects/{}/".format(self.research.id))
        title_div = self.browser.find_element_by_class_name("title-box")
        self.assertEqual(
         title_div.find_element_by_tag_name("h1").text, "Super Research"
        )
        self.assertEqual(
         title_div.find_element_by_class_name("total-time").text, "2 hours, 50 minutes"
        )


    def test_project_editing_requires_auth(self):
        self.get("/projects/{}/edit/".format(self.research.id))
        self.check_page("/")
        self.login()
        self.get("/projects/{}/edit/".format(self.running2.id))
        self.check_title("Not Found")
        self.get("/projects/9999999/edit/")
        self.check_title("Not Found")


    def test_can_delete_project(self):
        # User goes to project page
        self.login()
        self.get("/projects/")
        first_project = self.browser.find_elements_by_class_name("project")[0]
        self.click(first_project.find_element_by_tag_name("a"))

        # They go to edit the research project
        edit_link = self.browser.find_element_by_class_name("edit-link")
        self.click(edit_link)
        self.check_page("/projects/{}/edit/".format(self.research.id))
        self.check_title("Edit Project")

        # There is a link to the deletion page
        link = self.browser.find_element_by_class_name("delete-button")
        self.click(link)
        self.check_page("/projects/{}/delete/".format(self.research.id))
        self.check_title("Delete Project")

        # They can go back
        main = self.browser.find_element_by_tag_name("main")
        self.assertIn("are you sure", main.text.lower())
        self.assertIn("Research", main.text)
        self.assertIn("4 sessions", main.text)
        back_link = main.find_element_by_id("back-link")
        self.click(back_link)
        self.check_page("/projects/{}/edit/".format(self.research.id))
        self.check_title("Edit Project")

        # But they want to delete
        link = self.browser.find_element_by_class_name("delete-button")
        self.click(link)
        self.check_page("/projects/{}/delete/".format(self.research.id))
        self.check_title("Delete Project")
        delete = self.browser.find_element_by_class_name("delete-button")
        self.click(delete)
        self.check_page("/projects/")
        projects = self.browser.find_elements_by_class_name("project")
        self.assertEqual(len(projects), 7)
        for project in projects:
            self.assertNotIn("Research", project.text)


    def test_project_deletion_view_404(self):
        self.get("/projects/{}/delete/".format(self.research.id))
        self.check_page("/")
        self.login()
        self.get("/projects/{}/delete/".format(self.running2.id))
        self.check_title("Not Found")
        self.get("/projects/9999999/delete/")
        self.check_title("Not Found")
