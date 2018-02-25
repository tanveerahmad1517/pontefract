from django import forms
from .models import Session

class SessionForm(forms.ModelForm):

    project = forms.CharField()

    class Meta:
        model = Session
        fields = ["start", "end", "breaks"]
