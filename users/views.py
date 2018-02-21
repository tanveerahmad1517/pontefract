from django.shortcuts import render, redirect
import django.contrib.auth as auth
from users.forms import SignupForm

def signup(request):
    """This view handles requests to create an account.

    If the POST data it is sent is valid form data, the user will be created,
    logged in, and a redirect response will be returned for the home page.

    If it isn't valid, the invalid form will be returned, so this is not a view
    which a URL can be pointed at - it gets called by other views."""

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
        else:
            return form
    return redirect("/")
