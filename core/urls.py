from django.urls import path, include
import core.views as core_views
import projects.views as project_views

urlpatterns = [
 path(r"login/", core_views.login),
 path(r"policy/", core_views.policy),
 path(r"", core_views.root),
] + [
 path(r"logout/", core_views.logout),
 path(r"profile/<slug:page>/", core_views.profile),
 path(r"profile/", core_views.profile),
 path(r"delete-account/", core_views.delete_account),
 path(r"day/<slug:day>/", core_views.day),
] + [
 path(r"time/<slug:month>/", project_views.month),
 path(r"projects/new/", project_views.new_project),
 path(r"projects/<slug:project>/", project_views.project),
 path(r"projects/<slug:project>/edit/", project_views.edit_project),
 path(r"projects/<slug:project>/delete/", project_views.delete_project),
 path(r"sessions/<slug:session>/edit/", project_views.edit_session),
 path(r"sessions/<slug:session>/delete/", project_views.delete_session),
 path(r"projects/", project_views.projects),
]
