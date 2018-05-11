from testarsenal import DjangoTest
from core.templatetags import *

class TimeStringTests(DjangoTest):

    def test_can_convert_minutes(self):
        self.assertEqual(time_string(0), "0 minutes")
        self.assertEqual(time_string(1), "1 minute")
        self.assertEqual(time_string(30), "30 minutes")


    def test_can_convert_hours(self):
        self.assertEqual(time_string(60), "1 hour")
        self.assertEqual(time_string(61), "1 hour, 1 minute")
        self.assertEqual(time_string(90), "1 hour, 30 minutes")
        self.assertEqual(time_string(120), "2 hours")
        self.assertEqual(time_string(130), "2 hours, 10 minutes")
