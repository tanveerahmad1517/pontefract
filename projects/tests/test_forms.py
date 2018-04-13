from datetime import datetime, time
from unittest.mock import patch, Mock
from testarsenal import DjangoTest
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from django.forms.widgets import MultiWidget, Widget
from projects.forms import *

class ProjectFormTests(DjangoTest):

    def setUp(self):
        self.user = "USER"


    def test_project_form_has_correct_fields(self):
        form = ProjectForm(self.user)
        self.assertEqual(
         list(form.fields.keys()), [
          "name", "user"
         ])


    def test_name_field_can_obtain_data_from_datadict(self):
        self.assertEqual(
         ProjectForm(self.user).fields["name"].widget.value_from_datadict(
          {"project": "PPP"}, None, None
         ), "PPP"
        )


    @patch("projects.forms.forms.ModelForm.save")
    def test_project_form_can_handle_user(self, mock_save):
        model = Mock()
        mock_save.return_value = model
        form = ProjectForm(self.user)
        self.assertEqual(form.user, self.user)
        self.assertFalse(form.fields["user"].required)
        form.save()
        mock_save.assert_called_with(form, commit=False)
        self.assertEqual(model.user, self.user)
        model.save.assert_called_with()



class SessionFormTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("projects.forms.Project.objects.get")
        self.mock_get = self.patch1.start()
        self.mock_get.return_value = mixer.blend(Project)
        self.patch2 = patch("projects.forms.forms.ModelForm.clean")
        self.mock_clean = self.patch2.start()


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_session_form_has_correct_fields(self):
        form = SessionForm()
        self.assertEqual(
         list(form.fields.keys()), [
          "start_date", "end_date", "start_time", "end_time",
          "breaks", "project"
         ])


    def test_start_date_widget(self):
        widget = SessionForm().fields["start_date"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "1"})


    def test_start_time_widget(self):
        widget = SessionForm().fields["start_time"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "3"})


    def test_end_date_widget(self):
        widget = SessionForm().fields["end_date"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "2"})


    def test_end_time_widget(self):
        widget = SessionForm().fields["end_time"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "4"})


    def test_breaks_widget(self):
        widget = SessionForm().fields["breaks"].widget
        self.assertFalse(widget.is_required)
        self.assertEqual(widget.input_type, "number")
        self.assertEqual(widget.attrs, {"tabindex": "5"})
        self.assertEqual(
         widget.value_from_datadict({"breaks": ""}, 0, "breaks"), "0"
        )


    def test_projects_widget(self):
        widget = SessionForm().fields["project"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "text")
        self.assertEqual(widget.attrs, {"tabindex": "6"})


    def test_start_date_validation(self):
        start_date = SessionForm().fields["start_date"]
        self.assertTrue(start_date.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                start_date.clean(invalid)


    def test_start_time_validation(self):
        start_time = SessionForm().fields["start_time"]
        self.assertTrue(start_time.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                start_time.clean(invalid)


    def test_end_date_validation(self):
        end_date = SessionForm().fields["end_date"]
        self.assertTrue(end_date.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                end_date.clean(invalid)


    def test_end_time_validation(self):
        end_time = SessionForm().fields["end_time"]
        self.assertTrue(end_time.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                end_time.clean(invalid)


    def test_breaks_validation(self):
        breaks = SessionForm().fields["breaks"]
        self.assertFalse(breaks.required)
        for invalid in (-1, 0.4, "a\x00b"):
            with self.assertRaises(ValidationError):
                breaks.clean(invalid)


    def test_project_obtaining(self):
        self.mock_get.return_value = "RETURNED PROJECT"
        project = SessionForm(user="USER").fields["project"]
        self.assertEqual(project.to_python("abc"), "RETURNED PROJECT")
        self.mock_get.assert_called_with(name="abc", user="USER")


    def test_field_default_values(self):
        self.assertEqual(
         SessionForm().fields["start_date"].initial, datetime.now().date()
        )
        self.assertEqual(
         SessionForm().fields["end_date"].initial, datetime.now().date()
        )
        self.assertEqual(SessionForm().fields["breaks"].initial, 0)


    def test_can_reject_mismatched_times(self):
        form = SessionForm(data={
         "start_date": "2018-01-02", "start_time": "13:00",
         "end_date": "2018-01-02", "end_time": "12:00",
         "breaks": 10
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
