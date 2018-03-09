from datetime import datetime
from django import forms
from .models import Session

class DateInput(forms.widgets.DateInput):
    input_type = "date"



class TimeInput(forms.widgets.TimeInput):
    input_type = "time"



class SessionForm(forms.ModelForm):

    start_date = forms.DateField(initial=datetime.now().date(), widget=DateInput())
    end_date = forms.DateField(initial=datetime.now().date(), widget=DateInput())
    new_project = forms.CharField()

    class Meta:
        model = Session
        exclude = ["project"]

        widgets = {
         "start_time": TimeInput(),
         "end_time": TimeInput()
        }
