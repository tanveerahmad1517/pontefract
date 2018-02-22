from django.shortcuts import render, redirect
import django.contrib.auth as auth
from django.contrib.auth.models import User
from users.forms import SignupForm, LoginForm

def signup(request):
    """This view handles requests to create an account.

    If the POST data it is sent is valid form data, the user will be created,
    logged in, and a redirect response will be returned for the home page.

    If it isn't valid, the invalid form will be returned, so this is not a view
    which a URL can be pointed at - it gets called by other views."""

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create(
             username=form.data["username"],
             email=form.data["email"]
            )
            user.set_password(form.data["password"])
            user.save()
            auth.login(request, user)
        else:
            return form
    return redirect("/")


def login(request):
    """This view serves the login page on GET requests, and handles requests to
    log in on POST requests.

    It expects there to be a template called 'login.html' somewhere."""

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(
             username=form.data["username"], password=form.data["password"]
            )
            auth.login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html", {"form": form})
    form = LoginForm()
    return render(request, "login.html", {"form": form})
