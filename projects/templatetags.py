from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter(name="time_string")
def time_string(minutes):
    if minutes < 60:
        return "{} minute{}".format(minutes, "" if minutes == 1 else "s")
    else:
        hours = minutes // 60
        mins = minutes - (hours * 60)
        text = "{} hour{}".format(hours, "" if hours == 1 else "s")
        if mins:
            text += ", {} minute{}".format(mins, "" if mins == 1 else "s")
        return text
