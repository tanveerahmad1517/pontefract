from django.conf.urls import url
from users import views

urlpatterns = [
 url(r"^$", views.signup_page, name="signup_page")
]
