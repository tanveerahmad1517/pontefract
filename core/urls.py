from django.urls import path, include
import core.views as core_views

urlpatterns = [
 path(r"login/", core_views.login, name="login"),
 path(r"logout/", core_views.logout),
 path(r"time/<int:year>/<int:month>/", core_views.time_month),
 path(r"time/<int:year>/<int:month>/<int:day>/", core_views.time_day),
 path(r"projects/<int:pk>/", core_views.time_projects),
 path(r"projects/", core_views.projects),
 path(r"sessions/<int:pk>/", core_views.edit_session),
 path(r"", core_views.root),
]
