from datetime import datetime
from django import forms
from django.core.validators import MinValueValidator
from .models import Session, Project

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = []


    def __init__(self, user, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["user"].required = False
        self.fields["name"].widget.value_from_datadict = lambda d, f, n: d.get("project")
        self.user = user


    def save(self, *args, **kwargs):
        model = forms.ModelForm.save(self, *args, commit=False, **kwargs)
        model.user = self.user
        model.save()



class SessionForm(forms.ModelForm):
    """The form which allows a user to enter a session of work they have done.

    They can provide a new project at the same time."""

    project = forms.ModelChoiceField(
     queryset=Project.objects,
     widget=forms.widgets.TextInput(attrs={"tabindex": "6"})
    )

    class Meta:
        model = Session
        exclude = []

        widgets = {
         "start_date": forms.widgets.DateInput(attrs={"tabindex": "1"}),
         "start_time": forms.widgets.TimeInput(attrs={"tabindex": "3"}),
         "end_date": forms.widgets.DateInput(attrs={"tabindex": "2"}),
         "end_time": forms.widgets.TimeInput(attrs={"tabindex": "4"}),
         "breaks": forms.widgets.NumberInput(attrs={"tabindex": "5"})
        }

        widgets["start_date"].input_type = "date"
        widgets["start_time"].input_type = "time"
        widgets["end_date"].input_type = "date"
        widgets["end_time"].input_type = "time"
        widgets["breaks"].value_from_datadict = lambda d, f, n: d.get(n) or "0"


    def __init__(self, *args, user=None, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.user = user
        self.fields["start_date"].initial = datetime.now().date()
        self.fields["end_date"].initial = datetime.now().date()
        self.fields["breaks"].required = False
        self.fields["breaks"].widget.is_required = False
        self.fields["breaks"].validators.append(MinValueValidator(
         0, message="The break must be positive."
        ))
        self.fields["project"].to_python = lambda v: Project.objects.get(
         user=self.user, name=v
        )


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
        )).seconds <= self.cleaned_data.get("breaks", 0) * 60:
            self.add_error("breaks", "Break cannot cancel out session")
