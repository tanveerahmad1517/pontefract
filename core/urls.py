from django.urls import path, include
import core.views as core_views
import projects.views as project_views

urlpatterns = [
 path(r"login/", core_views.login),
 path(r"logout/", core_views.logout),
 path(r"profile/", core_views.profile),
 path(r"profile/time/", core_views.time_settings),
 path(r"profile/account/", core_views.account_settings),
 path(r"delete-account/", core_views.delete_account),
 path(r"time/<int:year>/<int:month>/", project_views.month),
 path(r"time/<int:year>/<int:month>/<int:day>/", project_views.day),
 path(r"projects/<int:pk>/", project_views.project),
 path(r"projects/", project_views.projects),
 path(r"sessions/<int:pk>/", project_views.edit_session),
 path(r"sessions/<int:pk>/delete/", project_views.delete_session),
 path(r"projects/new/", project_views.new_project),
 path(r"projects/<int:pk>/edit/", project_views.edit_project),
 path(r"projects/<int:pk>/delete/", project_views.delete_project),
 path(r"", core_views.root),
]
