from datetime import datetime, date
import pytz
from testarsenal import DjangoTest
from unittest.mock import Mock, patch
from mixer.backend.django import mixer
from django.core.exceptions import ValidationError
from django.utils import timezone as tz
from core.models import User
from projects.models import Project, Session

AUCK = pytz.timezone("Pacific/Auckland")

class UserTests(DjangoTest):

    def test_can_create_user(self):
        user = User(
         username="sam", email="sam@sam.sam", timezone="Europe/Paris",
         project_order="LD"
        )
        user.set_password("password")
        self.assertEqual(user.username, "sam")
        self.assertEqual(user.email, "sam@sam.sam")
        self.assertNotEqual(user.password, "password")
        self.assertEqual(user.timezone, "Europe/Paris")
        self.assertEqual(user.project_order, "LD")
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


    def test_default_project_order(self):
        user = User(username="sam", email="sam@sam.sam")
        self.assertEqual(user.project_order, "TD")


    def test_user_project_count(self):
        user = User.objects.create(username="sam", email="sam@sam.sam")
        for _ in range(4):
            mixer.blend(Project, user=user)
        for _ in range(3):
            mixer.blend(Project)
        self.assertEqual(user.project_count(), 4)


    @patch("projects.models.Session.objects.filter")
    def test_user_total_time(self, mock_filter):
        mock_filter.return_value = [Mock(duration=lambda: 50) for _ in range(5)]
        user = User.objects.create(username="sam", email="sam@sam.sam")
        self.assertEqual(user.total_time(), 250)
        mock_filter.assert_called_with(project__user=user)
