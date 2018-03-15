from datetime import datetime
from projects.models import Project
from .base import FunctionalTest

class SessionAddingTests(FunctionalTest):

    def fill_in_session_form(self, now, start_time, end_time, breaks, new_project=None, project=None, projects=()):
        # There is a form to record work
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_day_input = form.find_elements_by_tag_name("input")[0]
        start_time_input = form.find_elements_by_tag_name("input")[1]
        end_day_input = form.find_elements_by_tag_name("input")[2]
        end_time_input = form.find_elements_by_tag_name("input")[3]
        breaks_input = form.find_elements_by_tag_name("input")[4]
        new_project_input = form.find_elements_by_tag_name("input")[5]
        if projects:
            existing_project_input = form.find_element_by_tag_name("select")
        else:
            with self.assertRaises(self.NoElement):
                form.find_element_by_tag_name("select")

        # The form default values are sensible
        self.assertEqual(start_day_input.get_attribute("type"), "date")
        self.assertEqual(start_time_input.get_attribute("type"), "time")
        self.assertEqual(end_day_input.get_attribute("type"), "date")
        self.assertEqual(end_time_input.get_attribute("type"), "time")
        self.assertEqual(start_day_input.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(end_day_input.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(breaks_input.get_attribute("value"), "0")
        if project:
            self.assertEqual(self.get_select_values(existing_project_input), projects)

        # They enter some values and submit
        start_time_input.send_keys(start_time)
        end_time_input.send_keys(end_time)
        breaks_input.clear()
        if breaks != "0": breaks_input.send_keys(breaks)
        if new_project: new_project_input.send_keys(new_project)
        if project: self.select_dropdown(existing_project_input, project)
        submit = form.find_elements_by_tag_name("input")[-1]
        self.click(submit)


    def test_can_add_work_session(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = datetime.now()

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0635AM", "10", "Dog Walking", projects=False
        )

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_id("today-time-tracking")
        self.assertIn("20 minutes", today.text)

        # The session is there
        sessions = today.find_elements_by_class_name("session")
        self.assertEqual(len(sessions), 1)
        self.assertIn("Dog Walking", sessions[0].text)
        self.assertIn("06:05", sessions[0].text)
        self.assertIn("06:35", sessions[0].text)
        self.assertIn("10 minute", sessions[0].text)
        self.assertIn("20 minute", sessions[0].text)


    def test_can_add_work_session_to_existing_project(self):
        Project.objects.create(name="Running", user=self.user)
        Project.objects.create(name="Cycling", user=self.user)
        Project.objects.create(name="Swimming", user=self.user)

        # The user goes to the home page and fills out the form there
        self.login()
        self.get("/")
        now = datetime.now()
        self.fill_in_session_form(
         now, "1605PM", "1635PM", "0", project="Cycling",
         projects=["Running", "Cycling", "Swimming"]
        )

        # They are still on the main page
        self.check_page("/")

        # The total for the day is updated
        time = self.browser.find_element_by_id("user-time-tracking")
        today = time.find_element_by_id("today-time-tracking")
        self.assertIn("30 minutes", today.text)

        # The session is there
        sessions = today.find_elements_by_class_name("session")
        self.assertEqual(len(sessions), 1)
        self.assertIn("Cycling", sessions[0].text)
        self.assertIn("16:05", sessions[0].text)
        self.assertIn("16:35", sessions[0].text)
        self.assertIn("30 minute", sessions[0].text)
        self.assertNotIn("break", sessions[0].text)


    def test_second_time_must_be_after_first(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = datetime.now()

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0505AM", "10", "Dog Walking", projects=False
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
        error = form.find_element_by_id("end-time-error")
        self.assertIn("before", error.text)


    def test_breaks_must_be_positive(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = datetime.now()

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0705AM", "-10", "Dog Walking", projects=False
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
        now = datetime.now()

        # They fill out the session form that is there
        self.fill_in_session_form(
         now, "0605AM", "0705AM", "70", "Dog Walking", projects=False
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
