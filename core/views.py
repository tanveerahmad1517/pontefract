from django.shortcuts import render, redirect
from django.http import HttpResponse
from users.forms import SignupForm
from users.views import signup

def root(request):
    """The view that handles requests to the root URL. It hands the request to
    the landing view if the user is anonymous, and to the home view if they are
    logged in."""

    if request.user.is_authenticated:
        return home(request)
    return landing(request)


def landing(request):
    """The view that serves the landing page to logged out users."""

    if request.method == "POST":
        response = signup(request)
        if isinstance(response, HttpResponse):
            return response
        return render(request, "landing.html", {"form": response})
    form = SignupForm()
    return render(request, "landing.html", {"form": form})


def home(request):
    return render(request, "home.html")
