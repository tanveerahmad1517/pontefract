from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project

@login_required(login_url="/", redirect_field_name=None)
def day(request, year, month, day):
    """The view that responds to requests for a given time tracking day."""

    form = SessionForm(date=date(year, month, day))
    if request.method == "POST":
        form = process_session_form_data(request, date=date(year, month, day))
        if form.is_valid():
            form.save(request.user)
            return redirect("/time/{}/{}/{}/".format(year, month, day))
    day = Session.from_day(request.user, date(year, month, day))
    return render(request, "day.html", {"day": day, "form": form})


@login_required(login_url="/", redirect_field_name=None)
def month(request, year, month):
    """The view that responds to requests for a given time tracking month. If
    the month requested is before the user's first month, 404 is returned."""

    month_date, first_month = date(year, month, 1), request.user.first_month()
    if not first_month or month_date < first_month:
        raise Http404
    days = Session.from_month(request.user, year, month)
    return render(request, "month.html", {
     "month": date(year, month, 1),
     "days": days,
     "next": not days[0].next_month() > request.now.date(),
     "previous": not days[0].previous_month() < first_month
    })


@login_required(login_url="/", redirect_field_name=None)
def project(request, pk):
    """The view that responds to requests for a given time tracking month. If
    the user has no matching project, 404 is returned."""

    project = get_object_or_404(Project, id=pk, user=request.user)
    days = Session.from_project(project)
    return render(request, "project.html", {"project": project, "days": days})


@login_required(login_url="/", redirect_field_name=None)
def projects(request):
    """The view that sends all projects, sorted by total time spent on them."""

    projects = Project.by_total_duration(request.user)
    return render(request, "projects.html", {"projects": projects})


@login_required(login_url="/", redirect_field_name=None)
def edit_session(request, pk):
    """The view which lets users edit a session."""

    session = get_object_or_404(Session, id=pk, project__user=request.user)
    form = SessionForm(instance=session)
    if request.method == "POST":
        form = process_session_form_data(request, instance=session)
        if form.is_valid():
            form.save(request.user)
            return redirect(
             form.instance.local_start().strftime("/time/%Y/%m/%d/")
            )
    return render(request, "edit-session.html", {"form": form})


@login_required(login_url="/", redirect_field_name=None)
def delete_session(request, pk):
    """The view which lets users delete a session."""

    session = get_object_or_404(Session, id=pk, project__user=request.user)
    if request.method == "POST":
        session.delete()
        return redirect(session.local_start().strftime("/time/%Y/%m/%d/"))
    return render(request, "delete-session.html", {"session": session})
