from datetime import datetime
from django import forms
from .models import Session, Project

class DateInput(forms.widgets.DateInput):
    input_type = "date"



class TimeInput(forms.widgets.TimeInput):
    input_type = "time"



class SessionForm(forms.ModelForm):
    """The form which allows a user to enter a session of work they have done.

    They can provide a new project at the same time."""

    start_date = forms.DateField(
     initial=datetime.now().date(), widget=DateInput(attrs={"tabindex": "1"})
    )
    end_date = forms.DateField(
     initial=datetime.now().date(), widget=DateInput(attrs={"tabindex": "2"})
    )
    new_project = forms.CharField(widget=forms.widgets.TextInput(
     attrs={"autocomplete": "off", "tabindex": "7"}
    ))

    class Meta:
        model = Session
        exclude = []

        widgets = {
         "start_time": TimeInput(attrs={"tabindex": "3"}),
         "end_time": TimeInput(attrs={"tabindex": "4"}),
         "breaks": forms.widgets.NumberInput(attrs={"tabindex": "5"}),
        }

        error_messages = {
         "breaks": {"min_value": "Breaks must be positive"}
        }


    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["breaks"].required = False
        self.fields["project"].required = False
        self.fields["new_project"].required = False
        self.fields["project"].empty_label = None
        self.fields["project"].widget.attrs["tabindex"] = "6"


    def clean(self):
        forms.ModelForm.clean(self)
        if datetime.combine(
         self.cleaned_data["start_date"], self.cleaned_data["start_time"]
        ) > datetime.combine(
         self.cleaned_data["end_date"], self.cleaned_data["end_time"]
        ):
            self.add_error("end_date", "End time is before start time")
        elif (datetime.combine(
         self.cleaned_data["end_date"], self.cleaned_data["end_time"]
        ) - datetime.combine(
         self.cleaned_data["start_date"], self.cleaned_data["start_time"]
        )).seconds <= self.instance.breaks if self.instance.breaks else 0 * 60:
            self.add_error("breaks", "Break cannot cancel out session")


    def save(self, user, commit=True, **kwargs):
        """Gets a model object from the form data without saving it to the
        database, quickly creates a project object for it to belong to, adds the
        project to the session, and then commits the session to the database."""

        session = forms.ModelForm.save(self, commit=False)
        if self.cleaned_data.get("new_project"):
            project = Project.objects.create(
             name=self.cleaned_data["new_project"], user=user
            )
            project.save()
        else:
            project = self.cleaned_data["project"]
        session.project = project
        if session.breaks is None: session.breaks = 0
        session.save()
