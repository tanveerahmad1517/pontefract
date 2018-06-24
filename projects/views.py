from datetime import datetime, date, timedelta
from calendar import monthrange
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.db.models import F, ExpressionWrapper
from django.contrib.auth.decorators import login_required
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project, Day


def project(request, project):
    """Returns a view of a project by sending the relevant params to the time
    view."""

    return time(request, project=project)


def month(request, month):
    """Returns a view of a month by sending the relevant params to the time
    view."""

    year, month = [int(x) for x in month.split("-")]
    start = datetime(year, month, 1)
    end = datetime(year, month, monthrange(year, month)[1]) + timedelta(days=1)
    return time(request, start=start, end=end, as_month=start)


@login_required(login_url="/", redirect_field_name=None)
def time(request, start=None, end=None, project=None, as_month=False, all=False):
    """This view sends a list of sessions clustered into days. A few diverse
    URLs point to it."""

    sessions = Session.objects.filter(project__user=request.user).annotate(
     project_id=F("project"), project_name=F("project__name")
    )
    if project:
         project = get_object_or_404(Project, id=project, user=request.user)
         sessions = sessions.filter(project=project)
    if start:
        sessions = sessions.filter(start__gte=request.user.timezone.localize(start))
    if end:
        sessions = sessions.filter(start__lte=request.user.timezone.localize(end))
    days = Day.group_sessions_by_local_date(sessions.order_by("start"))
    if as_month: Day.insert_empty_month_days(days, as_month.year, as_month.month)
    return render(request, "time.html", {
     "days": days, "project": project, "month_date": as_month
    })


@login_required(login_url="/", redirect_field_name=None)
def projects(request):
    """The view that sends all projects, sorted by the user's custom sort
    order."""

    projects = Project.by_user_order(request.user)
    return render(request, "projects.html", {"projects": projects})


@login_required(login_url="/", redirect_field_name=None)
def edit_session(request, session):
    """The view which lets users edit a session."""

    session = get_object_or_404(Session, id=session, project__user=request.user)
    form = SessionForm(instance=session)
    if request.method == "POST":
        form = process_session_form_data(request, instance=session)
        if form.is_valid():
            form.save(request.user)
            return redirect(
             form.instance.local_start().strftime("/day/%Y-%m-%d/")
            )
    return render(request, "edit-session.html", {"form": form})


@login_required(login_url="/", redirect_field_name=None)
def delete_session(request, session):
    """The view which lets users delete a session."""

    session = get_object_or_404(Session, id=session, project__user=request.user)
    if request.method == "POST":
        session.delete()
        return redirect(session.local_start().strftime("/day/%Y-%m-%d/"))
    return render(request, "delete-session.html", {"session": session})


@login_required(login_url="/", redirect_field_name=None)
def new_project(request):
    """The view which lets users create a new project without having to make a
    new session."""

    form = ProjectForm(user=request.user)
    if request.method == "POST":
        form = ProjectForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("/projects/{}/".format(form.instance.id))
    return render(request, "new-project.html", {"form": form})


@login_required(login_url="/", redirect_field_name=None)
def edit_project(request, project):
    """The view which lets users edit a project."""

    project = get_object_or_404(Project, id=project, user=request.user)
    form = ProjectForm(user=request.user, instance=project)
    if request.method == "POST":
        form = ProjectForm(user=request.user, data=request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("/projects/{}/".format(form.instance.id))
    return render(request, "edit-project.html", {"form": form})


@login_required(login_url="/", redirect_field_name=None)
def delete_project(request, project):
    """The view which lets users delete a project."""

    project = get_object_or_404(Project, id=project, user=request.user)
    if request.method == "POST":
        project.delete()
        return redirect("/projects/")
    return render(request, "delete-project.html", {"project": project})
