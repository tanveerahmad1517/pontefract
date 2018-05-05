from datetime import datetime, date
from testarsenal import DjangoTest
from unittest.mock import Mock, patch
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import User
from projects.models import Project, Session

class UserTests(DjangoTest):

    def test_can_create_user(self):
        user = User(username="sam", email="sam@sam.sam", timezone="Europe/Paris")
        user.set_password("password")
        self.assertEqual(user.username, "sam")
        self.assertEqual(user.email, "sam@sam.sam")
        self.assertNotEqual(user.password, "password")
        self.assertEqual(user.timezone, "Europe/Paris")
        user.full_clean()


    def test_email_is_required(self):
        user = User(username="sam", timezone="Europe/Paris")
        user.set_password("password")
        with self.assertRaises(ValidationError):
            user.full_clean()


    def test_email_must_be_unique(self):
        user = User(username="sam", email="sam@sam.sam", timezone="Europe/Paris")
        user.save()
        user = User(username="sam2", email="sam@sam.sam", timezone="Europe/Paris")
        with self.assertRaises(ValidationError):
            user.full_clean()


    def test_default_timezone(self):
        user = User(username="sam", email="sam@sam.sam")
        self.assertEqual(str(user.timezone), "UTC")


    @patch("projects.models.Session.objects.filter")
    def test_user_first_session_month(self, mock_filter):
        filtered = Mock()
        sessions = [Mock(), Mock(), Mock()]
        filtered.order_by.return_value = sessions
        mock_filter.return_value = filtered
        sessions[0].local_start.return_value = date(1998, 6, 7)
        user = User(username="sam", email="sam@sam.sam", password="p")
        self.assertEqual(user.first_month(), date(1998, 6, 1))


    @patch("projects.models.Session.objects.filter")
    def test_user_first_session_month_none(self, mock_filter):
        mock_filter.return_value = []
        user = User(username="sam", email="sam@sam.sam", password="p")
        self.assertIsNone(user.first_month())


    def test_can_get_user_projects_sorted_by_duration(self):
        user = User(username="sam", email="sam@sam.sam", password="p")
        user.save()
        projects = [mixer.blend(Project, user=user) for _ in range(3)]
        sessions = [mixer.blend(Session, project=projects[i // 3]) for i in range(9)]
        print(sessions[0] is sessions[1])
        for i, session in enumerate(sessions):
            val = [3, 45, 5, 2, 7, 3, 23, 21, 100][i]
            print(val)
            session.duration = lambda s: val
            print(sessions[0].duration())
        print(sessions[1].duration())
        self.assertEqual(
         user.projects_by_time(), [projects[2], projects[0], projects[1]]
        )
