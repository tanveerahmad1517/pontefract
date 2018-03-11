from datetime import datetime
from testarsenal import DjangoTest
from unittest.mock import Mock, patch
from django.core.exceptions import ValidationError
from core.models import *

class UserTests(DjangoTest):

    def test_can_create_user(self):
        user = User(username="sam", email="sam@sam.sam")
        user.set_password("password")
        self.assertEqual(user.username, "sam")
        self.assertEqual(user.email, "sam@sam.sam")
        self.assertNotEqual(user.password, "password")
        user.full_clean()


    def test_email_is_required(self):
        user = User(username="sam")
        user.set_password("password")
        with self.assertRaises(ValidationError):
            user.full_clean()


    def test_email_must_be_unique(self):
        user = User(username="sam", email="sam@sam.sam", password="p")
        user.save()
        user = User(username="sam2", email="sam@sam.sam", password="p")
        with self.assertRaises(ValidationError):
            user.full_clean()


    @patch("projects.models.Session.objects.filter")
    def test_user_sessions_done_today(self, mock_filter):
        sessions = [Mock(), Mock(), Mock()]
        mock_filter.return_value = sessions
        user = User(username="sam", email="sam@sam.sam", password="p")
        self.assertEqual(sessions, user.sessions_today())
        mock_filter.assert_called_with(
         project__user=user, start_date=datetime.now().date()
        )


    @patch("core.models.User.sessions_today")
    def test_user_minutes_done_today(self, mock_sessions):
        sessions = [Mock(), Mock(), Mock()]
        sessions[0].duration.return_value = 4
        sessions[1].duration.return_value = 5
        sessions[2].duration.return_value = 6
        mock_sessions.return_value = sessions
        user = User(username="sam", email="sam@sam.sam", password="p")
        minutes = user.minutes_worked_today()
        mock_sessions.assert_called_with()
        self.assertEqual(minutes, 15)
