from django.shortcuts import render, redirect
from users.forms import SignupForm

def root(request):
    """The view that handles requests to the root URL. It hands the request to
    the landing view if the user is anonymous, and to the home view if they are
    logged in."""

    if request.user.is_authenticated:
        return home(request)
    return landing(request)


def landing(request):
    """The view that serves the landing page to logged out users."""

    form = SignupForm()
    return render(request, "landing.html", {"form": form})


def home(request):
    return render(request, "home.html")
