from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project

@login_required(login_url="/", redirect_field_name=None)
def time(request, month=None, project=None):
    """This view sends a list of sessions clustered into days. A few diverse
    URLs point to it."""
    
    month_date, title, days = None, None, None
    if month:
        month_date = date(*[int(x) for x in month.split("-")], 1)
        days = Session.from_month(request.user, month_date)
        title = month_date.strftime("%B %Y")
    if project:
         project = get_object_or_404(Project, id=project, user=request.user)
         days = Session.from_project(project)
         title = project.name
    return render(request, "time.html", {
     "title": title,
     "days": days,
     "month_date": month_date,
     "project": project
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
