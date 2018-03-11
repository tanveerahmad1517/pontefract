from django.shortcuts import render, redirect
from django.http import HttpResponse
import django.contrib.auth as auth
from core.forms import SignupForm, LoginForm
from projects.forms import SessionForm
from projects.models import Session

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
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect("/")
    return render(request, "landing.html", {"form": form})


def home(request):
    """The view that serves the home page to logged in users."""

    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save(request.user)
        return redirect("/")
    form = SessionForm()
    return render(request, "home.html", {
     "form": form,
    })


def login(request):
    """This view serves the login page on GET requests, and handles requests to
    log in on POST requests.
    It expects there to be a template called 'login.html' somewhere."""
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(
             username=form.data["username"], password=form.data["password"]
            )
            auth.login(request, user)
            return redirect("/")

    return render(request, "login.html", {"form": form})


def logout(request):
    """The logout view logs out any user who makes a POST request to this
    view."""

    if request.method == "POST":
        auth.logout(request)
    return redirect("/")
