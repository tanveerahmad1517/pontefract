from datetime import datetime
from unittest.mock import patch, Mock
from testarsenal import DjangoTest
from django.forms.widgets import MultiWidget, Widget
from projects.forms import *

class SessionFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("django.forms.ModelForm.save")
        self.patch2 = patch("projects.forms.Project.objects.create")
        self.patch3 = patch("django.forms.ModelForm.clean")
        self.mock_save = self.patch1.start()
        self.mock_create = self.patch2.start()
        self.mock_clean = self.patch3.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()
        self.patch3.stop()


    def test_session_form_has_correct_fields(self):
        form = SessionForm()
        self.assertEqual(
         list(form.fields.keys()), [
          "start_date", "end_date", "start_time", "end_time",
          "breaks", "project", "new_project"
         ])


    def test_start_date(self):
        start_date = SessionForm().fields["start_date"]
        self.assertEqual(start_date.initial, datetime.now().date())
        widget = start_date.widget
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "1"})


    def test_start_time(self):
        start_time = SessionForm().fields["start_time"]
        widget = start_time.widget
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "3"})


    def test_end_date(self):
        end_date = SessionForm().fields["end_date"]
        self.assertEqual(end_date.initial, datetime.now().date())
        widget = end_date.widget
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "2"})


    def test_end_time(self):
        end_time = SessionForm().fields["end_time"]
        widget = end_time.widget
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "4"})


    def test_breaks_field(self):
        breaks = SessionForm().fields["breaks"]
        self.assertEqual(breaks.initial, 0)
        self.assertFalse(breaks.required)
        widget = breaks.widget
        self.assertEqual(widget.input_type, "number")
        self.assertEqual(widget.attrs, {"tabindex": "5"})


    def test_project_field(self):
        project = SessionForm().fields["project"]
        self.assertFalse(project.required)
        self.assertIsNone(project.empty_label)
        widget = project.widget
        self.assertEqual(widget.input_type, "select")
        self.assertEqual(widget.attrs, {"tabindex": "6"})


    def test_new_project_field(self):
        new_project = SessionForm().fields["new_project"]
        self.assertFalse(new_project.required)
        widget = new_project.widget
        self.assertEqual(widget.input_type, "text")
        self.assertEqual(widget.attrs, {"autocomplete": "off", "tabindex": "7"})


    def test_can_reject_mismatched_times(self):
        form = SessionForm(data={
         "start_date": "2018-01-02", "start_time": "13:00",
         "end_date": "2018-01-02", "end_time": "12:00",
         "breaks": -10
        })
        self.assertFalse(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.assertIn("end_date", form.errors)


    def test_can_reject_break_longer_than_session(self):
        form = SessionForm(data={
         "start_date": "2018-01-02", "start_time": "12:00",
         "end_date": "2018-01-02", "end_time": "13:00",
         "breaks": 61
        })
        self.assertFalse(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.assertIn("breaks", form.errors)


    def test_session_saving_can_create_new_project(self):
        session, project = Mock(), Mock()
        self.mock_save.return_value = session
        self.mock_create.return_value = project
        form = SessionForm(data={"a": "b"})
        form.cleaned_data = {"new_project": "PPP"}
        form.save("USER")
        self.mock_save.assert_called_with(form, commit=False)
        self.mock_create.assert_called_with(name="PPP", user="USER")
        project.save.assert_called_with()
        self.assertIs(session.project, project)
        session.save.assert_called_with()


    def test_session_saving_can_create_use_project(self):
        session = Mock()
        self.mock_save.return_value = session
        form = SessionForm(data={"a": "b"})
        form.cleaned_data = {"project": "PPP"}
        form.save("USER")
        self.mock_save.assert_called_with(form, commit=False)
        self.assertFalse(self.mock_create.called)
        self.assertEqual(session.project, "PPP")
        session.save.assert_called_with()


    def test_session_saving_adds_0_break_if_none_given(self):
        session = Mock(name="session")
        session.breaks = None
        self.mock_save.return_value = session
        form = SessionForm(data={"a": "b"})
        form.cleaned_data = {"project": "PPP"}
        form.save("USER")
        self.assertEqual(session.breaks, 0)
