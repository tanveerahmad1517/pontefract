from django.shortcuts import render, redirect
import django.contrib.auth as auth
from users.forms import SignupForm

def signup(request):
    """This view handles requests to create an account."""

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
    return redirect("/")
