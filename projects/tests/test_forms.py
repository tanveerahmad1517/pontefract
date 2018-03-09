from datetime import datetime
from unittest.mock import patch, Mock
from testarsenal import DjangoTest
from django.forms.widgets import MultiWidget, Widget
from projects.forms import *

class SessionFormTests(DjangoTest):

    def test_session_form_has_correct_fields(self):
        form = SessionForm()
        self.assertEqual(
         list(form.fields.keys()),
         ["start_date", "end_date", "start_time", "end_time", "breaks", "new_project"]
        )


    def test_start_date_field(self):
        form = SessionForm()
        start_date = form.fields["start_date"]
        self.assertEqual(start_date.initial, datetime.now().date())
        widget = start_date.widget
        self.assertEqual(widget.input_type, "date")


    def test_end_date_field(self):
        form = SessionForm()
        end_date = form.fields["end_date"]
        self.assertEqual(end_date.initial, datetime.now().date())
        widget = end_date.widget
        self.assertEqual(widget.input_type, "date")


    def test_start_time_field(self):
        form = SessionForm()
        start_time = form.fields["start_time"]
        widget = start_time.widget
        self.assertEqual(widget.input_type, "time")


    def test_end_time_field(self):
        form = SessionForm()
        end_time = form.fields["end_time"]
        widget = end_time.widget
        self.assertEqual(widget.input_type, "time")


    def test_breaks_field(self):
        form = SessionForm()
        breaks = form.fields["breaks"]
        self.assertEqual(breaks.initial, 0)
        widget = breaks.widget
        self.assertEqual(widget.input_type, "number")


    def test_new_project_field(self):
        form = SessionForm()
        new_project = form.fields["new_project"]
        widget = new_project.widget
        self.assertEqual(widget.input_type, "text")
