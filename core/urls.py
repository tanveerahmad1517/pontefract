from django.urls import path, include
import core.views as core_views
#import users.views as user_views

urlpatterns = [
 path(r"login/", core_views.login, name="login"),
 path(r"logout/", core_views.logout),
 path(r"", core_views.root),
]
