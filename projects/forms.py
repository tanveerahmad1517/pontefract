from datetime import datetime
from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
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



class DateTimeWidget(forms.widgets.SplitDateTimeWidget):

    def decompress(*args, **kwargs):
        values = forms.widgets.SplitDateTimeWidget.decompress(*args, **kwargs)
        return (values[0], None)



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

        field_classes = {
        "start": forms.SplitDateTimeField, "end": forms.SplitDateTimeField
        }
        widgets = {
         "start": DateTimeWidget(
          date_attrs={"tabindex": "1"}, time_attrs={"tabindex": "3"}
         ),
         "end": DateTimeWidget(
          date_attrs={"tabindex": "2"}, time_attrs={"tabindex": "4"}
         ),
         "breaks": forms.widgets.NumberInput(attrs={"tabindex": "5"})
        }
        widgets["start"].widgets[0].input_type = "date"
        widgets["start"].widgets[1].input_type = "time"
        widgets["end"].widgets[0].input_type = "date"
        widgets["end"].widgets[1].input_type = "time"
        widgets["breaks"].value_from_datadict = lambda d, f, n: d.get(n) or "0"


    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["breaks"].required = False
        self.fields["breaks"].widget.is_required = False
        self.fields["breaks"].validators.append(MinValueValidator(
         0, message="The break must be positive."
        ))

        def to_python(value):
            try:
                return Project.objects.get(user=self.user, name=value)
            except Project.DoesNotExist:
                raise ValidationError("Invalid project name")
        self.fields["project"].to_python = to_python

        self.fields["start"].initial = timezone.localtime()
        self.fields["end"].initial = timezone.localtime()


    def clean(self):
        forms.ModelForm.clean(self)
        if self.cleaned_data["end"] < self.cleaned_data["start"]:
            self.add_error("end", "End time is before start time")
        elif (self.cleaned_data["end"] - self.cleaned_data["start"]
         ).seconds <= self.cleaned_data.get("breaks", 0) * 60:
            self.add_error("breaks", "Break cannot cancel out session")
