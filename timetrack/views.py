from django.shortcuts import render
from users.views import signup_page

# Create your views here.
def home_page(request):
    if not request.user.is_authenticated:
        return signup_page(request)
    return render(request, "home.html")
