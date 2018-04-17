from datetime import datetime, time
from mixer.backend.django import mixer
from unittest.mock import Mock, patch
from testarsenal import DjangoTest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from projects.models import *

class ProjectTests(DjangoTest):

    def setUp(self):
        self.user = mixer.blend(User)


    def test_can_create_project(self):
        project = Project(name="Basement Excavation", user=self.user)
        project.full_clean()


    def test_project_name_must_be_less_than_256(self):
        project = Project(name="." * 257, user=self.user)
        with self.assertRaises(ValidationError):
            project.full_clean()


    def test_project_name_must_be_unique_for_user(self):
        Project.objects.create(name="ABC", user=self.user)
        user2 = mixer.blend(User)
        Project.objects.create(name="ABCD", user=self.user)
        Project.objects.create(name="ABC", user=user2)
        with self.assertRaises(IntegrityError):
            Project.objects.create(name="ABC", user=self.user)


    def test_project_string_representation(self):
        project = Project(name="Basement Excavation", user=self.user)
        self.assertEqual(str(project), "Basement Excavation")


    def test_can_get_ordered_projects(self):
        user2 = mixer.blend(User)
        project1 = Project.objects.create(name="AAA", user=self.user)
        project2 = Project.objects.create(name="BBB", user=self.user)
        project3 = Project.objects.create(name="bbb", user=self.user)
        project4 = Project.objects.create(name="aaa", user=self.user)
        project5 = Project.objects.create(name="ccc", user=user2)
        projects = Project.by_name(self.user)
        self.assertEqual(projects.count(), 4)
        self.assertEqual(projects[0], project1)
        self.assertEqual(projects[1], project4)
        self.assertEqual(projects[2], project2)
        self.assertEqual(projects[3], project3)



class SessionTests(DjangoTest):

    def setUp(self):
        self.project = mixer.blend(Project)
        self.date1 = datetime(2008, 1, 1)
        self.date2 = datetime(2008, 1, 2)
        self.time1 = time(12, 15, 0)
        self.time2 = time(12, 30, 0)


    def test_can_create_session(self):
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         breaks=5, project=self.project
        )
        session.full_clean()


    def test_default_break_is_0(self):
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         project=self.project
        )
        session.full_clean()
        self.assertEqual(session.breaks, 0)


    def test_breaks_must_be_positive(self):
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         breaks=-5, project=self.project
        )
        with self.assertRaises(ValidationError): session.full_clean()


    @patch("projects.models.Session.objects.filter")
    @patch("projects.models.Session.duration_string")
    def test_can_get_sessions_from_day(self, mock_str, mock_filter):
        filtered = Mock()
        filtered.order_by.return_value = [10, 20, 30, 40]
        mock_filter.return_value = filtered
        mock_str.return_value = "STRING"
        sessions = Session.sessions_from("USER", "DAY")
        self.assertEqual(sessions, (
         "DAY", "STRING", [10, 20, 30, 40]
        ))
        mock_filter.assert_called_with(project__user="USER", start_date="DAY")
        filtered.order_by.assert_called_with("start_time")
        mock_str.assert_called_with(10, 20, 30, 40)


    @patch("projects.models.Session.objects.filter")
    @patch("projects.models.Session.duration_string")
    def test_can_get_sessions_grouped_by_date(self, mock_str, mock_filter):
        mock_sessions = [Mock() for _ in range(5)]
        mock_sessions[0].start_date = "A"
        mock_sessions[1].start_date = "A"
        mock_sessions[2].start_date = "B"
        mock_sessions[3].start_date = "B"
        mock_sessions[4].start_date = "B"
        filtered = Mock()
        filtered.order_by.return_value = mock_sessions
        mock_filter.return_value = filtered
        mock_str.side_effect = ("2", "3")
        sessions = Session.group_by_date("USER")
        mock_filter.assert_called_with(project__user="USER")
        filtered.order_by.assert_called_with("-start_date", "start_time")
        self.assertEqual(sessions, [
         ("A", "2", mock_sessions[:2]), ("B", "3", mock_sessions[2:])
        ])


    @patch("projects.models.Session.objects.filter")
    @patch("projects.models.Session.duration_string")
    def test_can_get_sessions_grouped_by_date_for_project(self, mock_str, mock_filter):
        mock_sessions = [Mock() for _ in range(5)]
        mock_sessions[0].start_date = "A"
        mock_sessions[1].start_date = "A"
        mock_sessions[2].start_date = "B"
        mock_sessions[3].start_date = "B"
        mock_sessions[4].start_date = "B"
        filtered1, filtered2 = Mock(), Mock()
        filtered2.order_by.return_value = mock_sessions
        mock_filter.return_value = filtered1
        filtered1.filter.return_value = filtered2
        mock_str.side_effect = ("2", "3")
        sessions = Session.group_by_date("USER", project="PROJECT")
        mock_filter.assert_called_with(project__user="USER")
        filtered1.filter.assert_called_with(project="PROJECT")
        filtered2.order_by.assert_called_with("-start_date", "start_time")
        self.assertEqual(sessions, [
         ("A", "2", mock_sessions[:2]), ("B", "3", mock_sessions[2:])
        ])


    @patch("projects.models.Session.objects.filter")
    @patch("projects.models.Session.duration_string")
    def test_can_get_sessions_grouped_by_date_for_month(self, mock_str, mock_filter):
        mock_sessions = [Mock(name=str(n)) for n in range(5)]
        mock_sessions[0].start_date = date(1990, 9, 1)
        mock_sessions[1].start_date = date(1990, 9, 1)
        mock_sessions[2].start_date = date(1990, 9, 1)
        mock_sessions[3].start_date = date(1990, 9, 2)
        mock_sessions[4].start_date = date(1990, 9, 2)
        filtered1, filtered2 = Mock(), Mock()
        filtered2.order_by.return_value = mock_sessions
        mock_filter.return_value = filtered1
        filtered1.filter.return_value = filtered2
        mock_str.return_value = "STRING"
        sessions = Session.group_by_date("USER", month=date(1990, 9, 1))
        mock_filter.assert_called_with(project__user="USER")
        filtered1.filter.assert_called_with(start_date__year=1990, start_date__month=9)
        filtered2.order_by.assert_called_with("-start_date", "start_time")
        self.assertEqual(sessions[::-1], [
         (date(1990, 9, 1), "STRING", mock_sessions[:3]),
         (date(1990, 9, 2), "STRING", mock_sessions[3:])] + [
         (date(1990, 9, n), "STRING", []) for n in range(3, 31)
        ])


    def test_can_get_start(self):
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         breaks=5, project=self.project
        )
        self.assertEqual(session.start(), datetime(2008, 1, 1, 12, 15))


    def test_can_get_end(self):
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         breaks=5, project=self.project
        )
        self.assertEqual(session.end(), datetime(2008, 1, 2, 12, 30))


    @patch("projects.models.Session.start")
    @patch("projects.models.Session.end")
    def test_can_get_duration(self, mock_end, mock_start):
        mock_start.return_value = datetime(2009, 5, 3, 15, 20)
        mock_end.return_value = datetime(2009, 5, 3, 16, 50)
        session = Session(
         start_date=self.date1, end_date=self.date2,
         start_time=self.time1, end_time=self.time2,
         breaks=5, project=self.project
        )
        self.assertEqual(session.duration(), 85)


    def test_can_get_duration_string(self):
        s1, s2, s3 = Mock(), Mock(), Mock()
        s1.duration.return_value = 1
        s2.duration.return_value = 0
        s3.duration.return_value = 0
        self.assertEqual(Session.duration_string(s1, s2, s3), "1 minute")
        s2.duration.return_value = 29
        self.assertEqual(Session.duration_string(s1, s2, s3), "30 minutes")
        s3.duration.return_value = 30
        self.assertEqual(Session.duration_string(s1, s2, s3), "1 hour")
        s3.duration.return_value = 31
        self.assertEqual(Session.duration_string(s1, s2, s3), "1 hour, 1 minute")
        s3.duration.return_value = 60
        self.assertEqual(Session.duration_string(s1, s2, s3), "1 hour, 30 minutes")
        s3.duration.return_value = 90
        self.assertEqual(Session.duration_string(s1, s2, s3), "2 hours")
        s3.duration.return_value = 100
        self.assertEqual(Session.duration_string(s1, s2, s3), "2 hours, 10 minutes")
