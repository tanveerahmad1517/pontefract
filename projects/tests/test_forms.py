from datetime import datetime, time, date
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
        self.assertEqual(list(form.fields.keys()), ["name"])


    def test_project_name_widget(self):
        widget = ProjectForm(self.user).fields["name"].widget
        self.assertEqual(widget.input_type, "text")
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.attrs, {
         "autocomplete": "off", "placeholder": "Project name"
        })


    def test_name_field_can_obtain_data_from_datadict(self):
        self.assertEqual(
         ProjectForm(self.user).fields["name"].widget.value_from_datadict(
          {"name": "NNN", "project": "PPP"}, None, None
         ), "NNN"
        )
        self.assertEqual(
         ProjectForm(self.user).fields["name"].widget.value_from_datadict(
          {"project": "PPP"}, None, None
         ), "PPP"
        )


    def test_name_validation(self):
        name = ProjectForm(self.user).fields["name"]
        self.assertTrue(name.required)
        for invalid in ("", None, "a\x00b", "   "):
            with self.assertRaises(ValidationError) as e:
                name.clean(invalid)
            if invalid == "   ":
                self.assertIn("valid", str(e.exception))


    @patch("projects.forms.forms.ModelForm.save")
    def test_project_form_can_handle_user(self, mock_save):
        model = Mock()
        mock_save.return_value = model
        form = ProjectForm(self.user)
        self.assertEqual(form.user, self.user)
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
         list(form.fields.keys()),
         ["start", "end", "timezone", "breaks", "project", "notes"]
        )


    def test_start_widget(self):
        widget = SessionForm().fields["start"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(
         widget.decompress(datetime(1990, 9, 30, 15, 30)),
         [date(1990, 9, 30), None]
        )
        widget.instance = 1
        self.assertEqual(
         widget.decompress(datetime(1990, 9, 30, 15, 30)),
         [date(1990, 9, 30), time(15, 30)]
        )


    def test_start_date_widget(self):
        widget = SessionForm().fields["start"].widget.widgets[0]
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "1"})


    def test_start_time_widget(self):
        widget = SessionForm().fields["start"].widget.widgets[1]
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "3"})
        self.assertEqual(widget.format_value(None), None)
        self.assertEqual(
         widget.format_value(datetime(1990, 9, 30, 15, 30, 11)), "15:30"
        )


    def test_end_widget(self):
        widget = SessionForm().fields["end"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(
         widget.decompress(datetime(1990, 9, 30, 15, 30)),
         [date(1990, 9, 30), None]
        )
        widget.instance = 1
        self.assertEqual(
         widget.decompress(datetime(1990, 9, 30, 15, 30)),
         [date(1990, 9, 30), time(15, 30)]
        )


    def test_end_date_widget(self):
        widget = SessionForm().fields["end"].widget.widgets[0]
        self.assertEqual(widget.input_type, "date")
        self.assertEqual(widget.attrs, {"tabindex": "2"})


    def test_end_time_widget(self):
        widget = SessionForm().fields["end"].widget.widgets[1]
        self.assertEqual(widget.input_type, "time")
        self.assertEqual(widget.attrs, {"tabindex": "4"})
        self.assertEqual(widget.format_value(None), None)
        self.assertEqual(
         widget.format_value(datetime(1990, 9, 30, 15, 30, 11)), "15:30"
        )


    def test_timezone_widget(self):
        user, user.timezone = Mock(), "TZ"
        widget = SessionForm(user=user).fields["timezone"].widget
        self.assertEqual(widget.value_from_datadict({}, None, None), "TZ")


    def test_breaks_widget(self):
        widget = SessionForm().fields["breaks"].widget
        self.assertEqual(widget.input_type, "number")
        self.assertFalse(widget.is_required)
        self.assertEqual(widget.attrs, {"tabindex": "5"})
        self.assertEqual(
         widget.value_from_datadict({"breaks": ""}, None, "breaks"), "0"
        )
        self.assertEqual(
         widget.value_from_datadict({}, None, "breaks"), "0"
        )
        self.assertEqual(widget.format_value(1), 1)
        self.assertEqual(widget.format_value(0), None)


    def test_projects_widget(self):
        self.mock_get.return_value = "PROJECT"
        widget = SessionForm(user="USER").fields["project"].widget
        self.assertTrue(widget.is_required)
        self.assertEqual(widget.input_type, "text")
        self.assertEqual(widget.attrs, {"tabindex": "6"})
        self.assertEqual(widget.format_value(None), None)
        self.assertEqual(widget.format_value("   "), None)
        self.assertEqual(widget.format_value(2), "PROJECT")
        self.mock_get.assert_called_with(id=2)
        self.assertEqual(widget.format_value("aaa"), "PROJECT")
        self.mock_get.assert_called_with(user="USER", name="aaa")


    def test_start_validation(self):
        start = SessionForm().fields["start"]
        self.assertTrue(start.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                start.clean(invalid)


    def test_end_validation(self):
        end = SessionForm().fields["end"]
        self.assertTrue(end.required)
        for invalid in ("", None, "a\x00b"):
            with self.assertRaises(ValidationError):
                end.clean(invalid)


    def test_breaks_validation(self):
        breaks = SessionForm().fields["breaks"]
        self.assertFalse(breaks.required)
        for invalid in (-1, 0.4, "a\x00b"):
            with self.assertRaises(ValidationError):
                breaks.clean(invalid)


    def test_project_validation(self):
        self.mock_get.side_effect = Project.DoesNotExist
        project = SessionForm(user="USER").fields["project"]
        self.assertTrue(project.required)
        for invalid in ("", None, "a\x00b", "     "):
            with self.assertRaises(ValidationError):
                project.to_python(invalid)


    def test_project_obtaining(self):
        self.mock_get.return_value = "RETURNED PROJECT"
        project = SessionForm(user="USER").fields["project"]
        self.assertEqual(project.to_python("abc"), "RETURNED PROJECT")
        self.mock_get.assert_called_with(name="abc", user="USER")


    def test_field_default_values(self):
        self.assertEqual(
         SessionForm().fields["start"].initial.date(), datetime.utcnow().date()
        )
        self.assertEqual(
         SessionForm().fields["end"].initial.date(), datetime.utcnow().date()
        )
        self.assertEqual(
         SessionForm(date=date(1990, 9, 28)).fields["start"].initial.date(), date(1990, 9, 28)
        )
        self.assertEqual(
         SessionForm(date=date(1990, 9, 28)).fields["end"].initial.date(), date(1990, 9, 28)
        )
        self.assertEqual(SessionForm().fields["breaks"].initial, None)


    def test_can_reject_mismatched_times(self):
        user, user.timezone = Mock(), "TZ"
        form = SessionForm(data={
         "start_0": "2018-01-02", "start_1": "13:00",
         "end_0": "2018-01-02", "end_1": "12:00",
         "breaks": 10
        }, user=user)
        self.assertFalse(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.assertIn("end", form.errors)


    def test_can_reject_break_longer_than_session(self):
        user, user.timezone = Mock(), "TZ"
        form = SessionForm(data={
         "start_0": "2018-01-02", "start_1": "12:00",
         "end_0": "2018-01-02", "end_1": "13:00",
         "breaks": 61
        }, user=user)
        self.assertFalse(form.is_valid())
        self.mock_clean.assert_called_with(form)
        self.assertIn("breaks", form.errors)



class SessionFormPostDataProcessingTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("projects.forms.ProjectForm")
        self.patch2 = patch("projects.forms.SessionForm")
        self.mock_project_form = self.patch1.start()
        self.mock_session_form = self.patch2.start()
        self.mock_project_form.return_value = Mock()
        self.mock_session_form.return_value = "SESSIONFORM"
        self.request = self.make_request("---", loggedin=True)


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_can_process_session_post_data_with_new_project(self):
        form = process_session_form_data(
         self.request, date=date(2001, 9, 11), instance="I"
        )
        self.assertEqual(form, "SESSIONFORM")
        self.mock_project_form.assert_called_with(self.request.user, self.request.POST)
        self.mock_project_form.return_value.save.assert_called_with()
        self.mock_session_form.assert_called_with(
         self.request.POST, user=self.request.user, date=date(2001, 9, 11), instance="I"
        )


    def test_can_process_session_post_data_with_existing_project(self):
        self.mock_project_form.return_value.save.side_effect = Exception
        form = process_session_form_data(
         self.request, date=date(2001, 9, 11), instance="I"
        )
        self.assertEqual(form, "SESSIONFORM")
        self.mock_project_form.assert_called_with(self.request.user, self.request.POST)
        self.mock_project_form.return_value.save.assert_called_with()
        self.mock_session_form.assert_called_with(
         self.request.POST, user=self.request.user, date=date(2001, 9, 11), instance="I"
        )
