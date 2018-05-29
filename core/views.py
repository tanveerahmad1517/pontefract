from datetime import date
from django.shortcuts import render, redirect
import django.contrib.auth as auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import Http404
from core.forms import *
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project

def root(request):
    """The view that handles requests to the root URL. It hands the request to
    the landing view if the user is anonymous, and to the home view if they are
    logged in."""

    if request.user.is_authenticated:
        return day(request, home=True)
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


def policy(request):
    """The view that serves the policy page."""

    return render(request, "policy.html")


@login_required(login_url="/", redirect_field_name=None)
def day(request, day=None, home=False):
    """The view that responds to requests for a given day."""

    try:
        day = date(*[int(x) for x in day.split("-")]) if day else request.now.date()
    except: raise Http404
    form = SessionForm(date=day)
    if request.method == "POST":
        form = process_session_form_data(request, date=day)
        if form.is_valid():
            form.save(request.user)
            return redirect("/" if home else day.strftime("/day/%Y-%m-%d/"))
    day = Session.from_day(request.user, day)
    return render(request, "day.html", {"day": day, "form": form, "home": home})


def logout(request):
    """The logout view logs out any user who makes a POST request to this
    view."""

    if request.method == "POST":
        auth.logout(request)
    return redirect("/")


@login_required(login_url="/", redirect_field_name=None)
def profile(request, page="profile"):
    """The view dealing with the user's profile."""

    context = {"page": page}
    if page in ("time", "account"):
        Form = TimeSettingsForm if page == "time" else AccountSettingsForm
        context["form"] = Form(instance=request.user)
        if request.method == "POST":
            context["form"] = Form(request.POST, instance=request.user)
            if context["form"].is_valid():
                context["form"].save()
                if page == "account":
                    update_session_auth_hash(request, context["form"].instance)
                return redirect(f"/profile/{page}/")
    return render(request, "profile.html", context)


@login_required(login_url="/", redirect_field_name=None)
def delete_account(request):
    """The view dealing with deleting a user account."""

    error = False
    if request.method == "POST":
        if request.user.check_password(request.POST["password"]):
            request.user.delete()
            return redirect("/")
        else: error = "Invalid credentials"
    return render(request, "delete-account.html", {"error": error})
