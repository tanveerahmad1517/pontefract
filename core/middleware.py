import pytz
from datetime import datetime
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try: timezone.activate(request.user.timezone)
        except: pass
        request.now = timezone.localtime()
