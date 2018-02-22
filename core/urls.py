from django.urls import path, include
import core.views as core_views
import users.views as user_views

urlpatterns = [
 path(r"login/", user_views.login, name="login"),
 path(r"", core_views.root),
]
