from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import UserForm

def root(request):
    """The view which handles requests to the root URL."""

    if request.user.is_authenticated:
        return home(request)
    return signup(request)


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
        else:
            return render(request, "signup.html", {"form": form})
    form = UserForm()
    return render(request, "signup.html", {"form": form})


def home(request):
    return render(request, "home.html")
