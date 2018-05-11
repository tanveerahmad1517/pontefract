import pytz
from datetime import datetime
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """When a request comes in, activate the user's timezone to override the
        settings default, and add the current time in the user's local time to
        the request."""
        
        try: timezone.activate(request.user.timezone)
        except: pass
        request.now = timezone.localtime()
