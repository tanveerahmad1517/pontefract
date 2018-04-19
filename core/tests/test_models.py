from datetime import datetime
from testarsenal import DjangoTest
from unittest.mock import Mock, patch
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import *

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
