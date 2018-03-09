from datetime import datetime
from .base import FunctionalTest

class SessionAddingTests(FunctionalTest):

    def test_can_add_work_session(self):
        # User goes to the home page
        self.login()
        self.get("/")
        now = datetime.now()

        # There is a form to record work
        time = self.browser.find_element_by_id("user-time-tracking")
        form = time.find_element_by_tag_name("form")
        start_day = form.find_elements_by_tag_name("input")[0]
        start_time = form.find_elements_by_tag_name("input")[1]
        end_day = form.find_elements_by_tag_name("input")[2]
        end_time = form.find_elements_by_tag_name("input")[3]
        breaks = form.find_elements_by_tag_name("input")[4]
        project = form.find_elements_by_tag_name("input")[5]

        # The form default values are sensible
        self.assertEqual(start_day.get_attribute("type"), "date")
        self.assertEqual(start_time.get_attribute("type"), "time")
        self.assertEqual(end_day.get_attribute("type"), "date")
        self.assertEqual(end_time.get_attribute("type"), "time")
        self.assertEqual(start_day.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(end_day.get_attribute("value"), now.date().strftime("%Y-%m-%d"))
        self.assertEqual(breaks.get_attribute("value"), "0")
