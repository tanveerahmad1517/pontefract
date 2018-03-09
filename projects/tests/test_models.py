from datetime import datetime, time
from mixer.backend.django import mixer
from testarsenal import DjangoTest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
