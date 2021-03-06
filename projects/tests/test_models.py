from datetime import datetime, time, date
import pytz
from mixer.backend.django import mixer
from unittest.mock import Mock, patch
from testarsenal import DjangoTest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from projects.models import *

AUCK = pytz.timezone("Pacific/Auckland")

class ProjectTests(DjangoTest):

    def setUp(self):
        self.user = mixer.blend(User)


    def test_can_create_project(self):
        project = Project(name="Basement Excavation", user=self.user)
        project.full_clean()


    def test_project_name_must_be_less_than_255(self):
        project = Project(name="." * 256, user=self.user)
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
        projects = Project.objects.filter(user=self.user)
        self.assertEqual(projects.count(), 4)
        self.assertEqual(projects[0], project1)
        self.assertEqual(projects[1], project4)
        self.assertEqual(projects[2], project2)
        self.assertEqual(projects[3], project3)


    @patch("projects.models.Project.session_set")
    def test_total_project_time(self, mock_set):
        mock_set.all.return_value = [Mock(), Mock(), Mock()]
        mock_set.all.return_value[0].duration.return_value = 10
        mock_set.all.return_value[1].duration.return_value = 20
        mock_set.all.return_value[2].duration.return_value = 19
        project = Project.objects.create(name="AAA", user=self.user)
        self.assertEqual(project.total_time(), 49)
        mock_set.all.assert_called_with()


    def test_can_get_projects_by_total_duration(self):
        user1, user2 = mixer.blend(User), mixer.blend(User)
        projects = [Project.objects.create(name=str(i), user=user1) for i in range(4)]
        projects.append(Project.objects.create(name="4", user=user2))
        sessions = [mixer.blend(
         Session, project=projects[i // 2], breaks = 40 if i == 1 else i * 5,
         start=datetime(2008, 1, 1, 9, 15, 0, tzinfo=pytz.timezone("UTC")),
         end=datetime(2008, 1, 1, 10, i, 0, tzinfo=pytz.timezone("UTC"))
        ) for i in range(10)]
        ordered = list(Project.by_user_order(user1))
        self.assertEqual(
         ordered, [projects[1], projects[2], projects[0], projects[3]]
        )
        self.assertEqual(ordered[0].duration, (47 + 48) - 25)
        self.assertEqual(ordered[1].duration, 49 + 50 - 45)
        self.assertEqual(ordered[2].duration, 45 + 46 - 40)
        self.assertEqual(ordered[3].duration, 51 + 52 - 65)
        self.assertEqual(ordered[0].recent, sessions[3])
        self.assertEqual(ordered[1].recent, sessions[5])
        self.assertEqual(ordered[2].recent, sessions[1])
        self.assertEqual(ordered[3].recent, sessions[7])


    def test_can_get_projects_by_last_done(self):
        user1, user2 = mixer.blend(User, project_order="LD"), mixer.blend(User)
        projects = [Project.objects.create(name=str(i), user=user1) for i in range(4)]
        projects.append(Project.objects.create(name="4", user=user1))
        projects.append(Project.objects.create(name="5", user=user2))
        sessions = [mixer.blend(
         Session, project=projects[i // 2], breaks = 40 if i == 1 else i * 5,
         start=datetime(2008, 1, 1, 9, i, 0, tzinfo=pytz.timezone("UTC")),
         end=datetime(2008, 1, 1, 10, i, 0, tzinfo=pytz.timezone("UTC"))
        ) for i in range(10)]
        ordered = list(Project.by_user_order(user1))
        self.assertEqual(ordered, projects[:5][::-1])



class SessionTests(DjangoTest):

    def setUp(self):
        self.user = mixer.blend(User)
        self.project = mixer.blend(Project, user=self.user)
        self.dt1 = datetime(
         2008, 1, 1, 9, 15, 0, tzinfo=AUCK
        )
        self.dt2 = datetime(
         2008, 1, 1, 9, 30, 0, tzinfo=AUCK
        )
        self.dt3 = datetime(
         2009, 1, 1, 9, 45, 0, tzinfo=AUCK
        )


    def test_can_create_session(self):
        session = Session(
         start=self.dt1, end=self.dt2, breaks=5, project=self.project,
         timezone=AUCK, notes="A good session."
        )
        session.full_clean(), session.save()


    def test_default_break_is_0(self):
        session = Session(
         start=self.dt1, end=self.dt2, project=self.project,
         timezone=AUCK
        )
        session.full_clean(), session.save()
        self.assertEqual(session.breaks, 0)


    def test_breaks_must_be_positive(self):
        session = Session(
         start=self.dt1, end=self.dt2, breaks=-5, project=self.project,
         timezone=AUCK
        )
        with self.assertRaises(ValidationError): session.full_clean()


    def test_notes_not_required(self):
        session = Session(
         start=self.dt1, end=self.dt2, breaks=5, project=self.project,
         timezone=AUCK
        )
        session.full_clean(), session.save()


    def test_start_local_timezone(self):
        session = Session(
         start=datetime(2008, 1, 1, 12, 0, tzinfo=pytz.UTC),
         end=datetime(2008, 1, 1, 12, 30, tzinfo=pytz.UTC),
         breaks=5, project=self.project,
         timezone=AUCK
        )
        tz.activate(AUCK)
        self.assertEqual(str(session.start.tzinfo), "UTC")
        self.assertEqual(str(session.local_start().tzinfo), "Pacific/Auckland")


    def test_end_local_timezone(self):
        session = Session(
         start=datetime(2008, 1, 1, 12, 0, tzinfo=pytz.UTC),
         end=datetime(2008, 1, 1, 12, 30, tzinfo=pytz.UTC),
         breaks=5, project=self.project,
         timezone=AUCK
        )
        tz.activate(AUCK)
        self.assertEqual(str(session.end.tzinfo), "UTC")
        self.assertEqual(str(session.local_end().tzinfo), "Pacific/Auckland")


    def test_can_get_duration(self):
        session = Session(
         start=self.dt1, end=self.dt2, breaks=5, project=self.project
        )
        self.assertEqual(session.duration(), 10)


    def test_can_get_long_duration(self):
        session = Session(
         start=self.dt1, end=self.dt3, breaks=5, project=self.project
        )
        self.assertEqual(session.duration(), 527065)


    @patch("projects.models.Day")
    def test_can_get_sessions_from_day(self, mock_day):
        mock_day.return_value = "DAY"
        for hour in (10, 13):
            Session.objects.create(
             start=datetime(
              2007, 1, 10, hour, 5, 0, tzinfo=AUCK
             ), end=self.dt3, project=self.project,
             timezone=AUCK
            )
        self.assertEqual(Session.from_day(self.user, date(2007, 1, 9)), "DAY")
        self.assertEqual(
         list(mock_day.call_args_list[0][0][0]), list(Session.objects.filter(id=1))
        )
        self.assertEqual(mock_day.call_args_list[0][1]["day"], date(2007, 1, 9))
        sessions = Session.from_day(self.user, date(2007, 1, 10))
        self.assertEqual(
         list(mock_day.call_args_list[1][0][0]), list(Session.objects.filter(id=2))
        )
        with tz.override(AUCK):
            sessions = Session.from_day(self.user, date(2007, 1, 10))
            self.assertEqual(
             list(mock_day.call_args_list[2][0][0]), list(Session.objects.all())
            )



class DayTests(DjangoTest):

    def setUp(self):
        self.sessions = [Mock() for _ in range(10)]
        for i, session in enumerate(self.sessions):
            session.duration.return_value = i + 1


    def test_day_creation_tests(self):
        day = Day(self.sessions, day=date(1996, 3, 4))
        self.assertEqual(day.sessions, self.sessions)
        self.assertEqual(day.day, date(1996, 3, 4))
        self.assertEqual(day.total_duration, 55)


    def test_day_iteration(self):
        day = Day(self.sessions, day=date(1996, 3, 4))
        self.assertEqual(list(day), self.sessions)


    def test_yesterday(self):
        self.assertEqual(
         Day(self.sessions, day=date(1996, 3, 4)).yesterday(), date(1996, 3, 3)
        )
        self.assertEqual(
         Day(self.sessions, day=date(1996, 1, 1)).yesterday(), date(1995, 12, 31)
        )


    def test_tomorrow(self):
        self.assertEqual(
         Day(self.sessions, day=date(1996, 3, 4)).tomorrow(), date(1996, 3, 5)
        )
        self.assertEqual(
         Day(self.sessions, day=date(1996, 2, 28)).tomorrow(), date(1996, 2, 29)
        )
        self.assertEqual(
         Day(self.sessions, day=date(1996, 12, 31)).tomorrow(), date(1997, 1, 1)
        )


    def test_previous_month(self):
        self.assertEqual(
         Day(self.sessions, day=date(1996, 3, 4)).previous_month(), date(1996, 2, 1)
        )
        self.assertEqual(
         Day(self.sessions, day=date(1996, 1, 31)).previous_month(), date(1995, 12, 1)
        )


    def test_next_month(self):
        self.assertEqual(
         Day(self.sessions, day=date(1996, 3, 4)).next_month(), date(1996, 4, 1)
        )
        self.assertEqual(
         Day(self.sessions, day=date(1996, 12, 31)).next_month(), date(1997, 1, 1)
        )


    @patch("projects.models.Day")
    def test_day_grouping(self, mock_day):
        mock_days = [Mock(day=i) for i in range(4)]
        mock_day.side_effect = mock_days
        s1 = mixer.blend(Session, start=datetime(1978, 2, 4, 8, 0, 0, tzinfo=AUCK))
        s2 = mixer.blend(Session, start=datetime(1978, 2, 4, 18, 0, 0, tzinfo=AUCK))
        s3 = mixer.blend(Session, start=datetime(1978, 2, 5, 1, 0, 0, tzinfo=AUCK))
        s4 = mixer.blend(Session, start=datetime(1978, 2, 5, 18, 0, 0, tzinfo=AUCK))
        s5 = mixer.blend(Session, start=datetime(1978, 2, 6, 7, 0, 0, tzinfo=AUCK))
        s6 = mixer.blend(Session, start=datetime(1978, 2, 6, 19, 0, 0, tzinfo=AUCK))
        days = Day.group_sessions_by_local_date([s1, s2, s3, s4, s5, s6])
        self.assertEqual(days, mock_days[::-1])
        mock_day.assert_any_call([s1], day=date(1978, 2, 3))
        mock_day.assert_any_call([s2, s3], day=date(1978, 2, 4))
        mock_day.assert_any_call([s4, s5], day=date(1978, 2, 5))
        mock_day.assert_any_call([s6], day=date(1978, 2, 6))


    @patch("projects.models.Day")
    def test_day_insertion(self, mock_day):
        mock_day.side_effect = lambda s, **d: Mock(day=d["day"])
        days = [Mock(day=date(1986, 2, i)) for i in [2, 4, 6, 11, 15, 23]][::-1]
        Day.insert_empty_month_days(days, 1986, 2)
        self.assertEqual(len(days), 28)
        self.assertEqual([d.day.day for d in days], list(range(1, 29))[::-1])


    @patch("projects.models.Day")
    @patch("projects.models.tz.localtime")
    def test_day_insertion_stops_today(self, mock_local, mock_day):
        mock_local.return_value = datetime(1986, 2, 11)
        mock_day.side_effect = lambda s, **d: Mock(day=d["day"])
        days = [Mock(day=date(1986, 2, i)) for i in [2, 4, 6, 11, 15, 23]][::-1]
        Day.insert_empty_month_days(days, 1986, 2)
        self.assertEqual(len(days), 11)
        self.assertEqual([d.day.day for d in days], list(range(1, 12))[::-1])
