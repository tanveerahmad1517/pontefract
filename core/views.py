from django.shortcuts import render, redirect

def root(request):
    return signup(request)


def signup(request):
    return render(request, "signup.html")
