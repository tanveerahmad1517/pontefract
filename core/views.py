from django.shortcuts import render, redirect

def root(request):
    """The view which handles requests to the root URL."""

    return signup(request)


def signup(request):
    return render(request, "signup.html")
