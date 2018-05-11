from testarsenal import DjangoTest
from unittest.mock import Mock, patch
from core.middleware import *

class TimezoneMiddlewareTests(DjangoTest):

    @patch("core.middleware.timezone")
    def test_can_add_timezome_info_to_requests(self, mock_tz):
        request = Mock()
        middleware = TimezoneMiddleware()
        middleware.process_request(request)
        mock_tz.activate.assert_called_with(request.user.timezone)
        self.assertEqual(request.now, mock_tz.localtime())
