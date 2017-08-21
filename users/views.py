from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def signup_page(request):
    if request.method == "POST":
        user = User.objects.create_user(
         email=request.POST["email"],
         password=request.POST["password"],
         username=request.POST["username"]
        )
        login(request, user)
        return redirect("/")
    return render(request, "signup.html")


def login_page(request):
    if request.method == "POST":
        user = authenticate(
         username=request.POST["username"],
         password=request.POST["password"]
        )
        if user:
            login(request, user)
    return redirect("/")


def logout_page(request):
    logout(request)
    return redirect("/")
