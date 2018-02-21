from django.shortcuts import render, redirect
from users.forms import SignupForm

def root(request):
    return signup(request)


def signup(request):
    form = SignupForm()
    return render(request, "landing.html", {"form": form})
