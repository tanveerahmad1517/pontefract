from datetime import datetime
from django import forms
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from .models import Session, Project

class ProjectNameWidget(forms.TextInput):
    """The name widget for a Project Form. As this form is never rendered, the
    only thing this widget has to do is find the relevant string from a data
    dictionary when saving a project.

    This has to be overridden because by default it would look for a key called
    'name' but in practice this form will be used to parse POST data from a
    Session form, where the name is a key called 'project'."""

    def value_from_datadict(self, data, files, name):
        """Takes a POST dictionary from a SessionForm and returns the string
        containing the project name."""

        name =  data.get("project")
        return name



class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        exclude = []
        widgets = {"name": ProjectNameWidget()}


    def __init__(self, user, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["user"].required = False
        self.user = user


    def save(self, *args, **kwargs):
        model = forms.ModelForm.save(self, *args, commit=False, **kwargs)
        model.user = self.user
        model.save()



class DateWidget(forms.DateInput):

    input_type = "date"



class TimeWidget(forms.TimeInput):

    input_type = "time"

    def format_value(self, value):
        value = forms.TimeInput.format_value(self, value)
        return value [:5] if isinstance(value, str) else value



class DateTimeWidget(forms.SplitDateTimeWidget):

    def __init__(self, *args, **kwargs):
        forms.SplitDateTimeWidget.__init__(self, *args, **kwargs)
        self.widgets = (DateWidget(), TimeWidget())
        self.instance = False


    def decompress(self, *args, **kwargs):
        values = forms.SplitDateTimeWidget.decompress(self, *args, **kwargs)
        return values if self.instance else (values[0], None)



class DateTimeField(forms.SplitDateTimeField):

    def __init__(self, *args, **kwargs):
        forms.SplitDateTimeField.__init__(self, *args, **kwargs)
        self.initial = timezone.localtime()



class SessionBreaksField(forms.IntegerField):

    def __init__(self, *args, **kwargs):
        forms.IntegerField.__init__(self, *args, **kwargs)
        self.required = False
        self.validators.append(MinValueValidator(
         0, message="The break must be positive."
        ))


class SessionBreaksWidget(forms.NumberInput):

    def __init__(self, *args, **kwargs):
        forms.NumberInput.__init__(self, *args, **kwargs)
        self.is_required = False


    def value_from_datadict(self, data, files, name):
        return data.get(name) or "0"



class SessionProjectField(forms.ModelChoiceField):

    def __init__(self, *args, **kwargs):
        forms.ModelChoiceField.__init__(self, *args, **kwargs)
        self.user = None
        self.queryset = Project.objects


    def to_python(self, value):
        try:
            return Project.objects.get(user=self.user, name=value)
        except Project.DoesNotExist:
            raise ValidationError("Invalid project name")



class SessionProjectWidget(forms.TextInput):

    def __init__(self, *args, **kwargs):
        forms.TextInput.__init__(self, *args, **kwargs)
        self.user = None


    def format_value(self, value):
        if value:
            if isinstance(value, int):
                return Project.objects.get(id=value)
            elif value.strip():
                return Project.objects.get(user=self.user, name=value)



class SessionForm(forms.ModelForm):
    """The form which allows a user to enter a session of work they have done.

    They can provide a new project at the same time."""

    class Meta:
        model = Session
        exclude = []

        field_classes = {
         "start": DateTimeField, "end": DateTimeField,
         "breaks": SessionBreaksField, "project": SessionProjectField
        }

        widgets = {
         "start": DateTimeWidget(
          date_attrs={"tabindex": "1"}, time_attrs={"tabindex": "3"},
         ),
         "end": DateTimeWidget(
          date_attrs={"tabindex": "2"}, time_attrs={"tabindex": "4"}
         ),
         "breaks": SessionBreaksWidget(attrs={"tabindex": "5"}),
         "project": SessionProjectWidget(attrs={"tabindex": "6"})
        }


    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields["start"].widget.instance = self.instance.id is not None
        self.fields["end"].widget.instance = self.instance.id is not None
        self.fields["project"].user = self.user
        self.fields["project"].widget.user = self.user


    def clean(self):
        forms.ModelForm.clean(self)
        if "start" in self.cleaned_data and "end" in self.cleaned_data:
            if self.cleaned_data["end"] < self.cleaned_data["start"]:
                self.add_error("end", "End time is before start time")
            elif (self.cleaned_data["end"] - self.cleaned_data["start"]
             ).seconds <= self.cleaned_data.get("breaks", 0) * 60:
                self.add_error("breaks", "Break cannot cancel out session")
