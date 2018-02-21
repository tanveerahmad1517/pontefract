from django.urls import path, include
import core.views as core_views
import users.views as user_views

urlpatterns = [
 path(r"signup/", user_views.signup, name="signup"),
 path(r"", core_views.root),
]
