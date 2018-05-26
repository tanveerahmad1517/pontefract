from datetime import date
from django.shortcuts import render, redirect
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required
from core.forms import *
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project

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

    form = SessionForm()
    if request.method == "POST":
        form = process_session_form_data(request)
        if form.is_valid():
            form.save(request.user)
            return redirect("/")
    day = Session.from_day(request.user, request.now.date())
    return render(request, "home.html", {"form": form, "day": day})


def login(request):
    """This view serves the login page on GET requests, and handles requests to
    log in on POST requests.
    It expects there to be a template called 'login.html' somewhere."""

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = form.validate_credentials()
        if user:
            auth.login(request, user)
            return redirect("/")
    return render(request, "login.html", {"form": form})


def logout(request):
    """The logout view logs out any user who makes a POST request to this
    view."""

    if request.method == "POST":
        auth.logout(request)
    return redirect("/")


@login_required(login_url="/", redirect_field_name=None)
def profile(request):
    """The view dealing with the user's profile."""

    return render(request, "profile.html", {"page": "profile"})


@login_required(login_url="/", redirect_field_name=None)
def time_settings(request):
    """The view dealing with the user's time tracking settings."""

    form = TimeSettingsForm(instance=request.user)
    if request.method == "POST":
        form = TimeSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("/profile/time/")
    return render(request, "profile.html", {"page": "time", "form": form})


@login_required(login_url="/", redirect_field_name=None)
def account_settings(request):
    """The view dealing with the user's account settings."""

    form = AccountSettingsForm(instance=request.user)
    if request.method == "POST":
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            auth.update_session_auth_hash(request, form.instance)
            return redirect("/profile/account/")
    return render(request, "profile.html", {"page": "account", "form": form})


@login_required(login_url="/", redirect_field_name=None)
def delete_account(request):
    """The view dealing with deleting a user account."""

    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        user = form.validate_credentials(user_to_match=request.user)
        if user:
            user.delete()
            return redirect("/")
    return render(request, "delete-account.html", {"form": form})
