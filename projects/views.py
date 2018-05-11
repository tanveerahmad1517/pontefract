from datetime import date, timedelta
from calendar import monthrange
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.forms import SignupForm, LoginForm
from projects.forms import SessionForm, ProjectForm, process_session_form_data
from projects.models import Session, Project


@login_required(login_url="/", redirect_field_name=None)
def month(request, year, month):
    month_date, first_month = date(year, month, 1), request.user.first_month()
    if not first_month or month_date < first_month:
        raise Http404
    days = Session.from_month(request.user, year, month)
    return render(request, "time-tracking-month.html", {
     "month": date(year, month, 1),
     "days": days,
     "next": not days[0].next_month() > request.now.date(),
     "previous": not days[0].previous_month() < first_month
    })


@login_required(login_url="/", redirect_field_name=None)
def project(request, pk):
    try:
        project = Project.objects.get(id=pk, user=request.user)
    except Project.DoesNotExist: raise Http404
    days = Session.from_project(project)
    return render(request, "project.html", {"project": project, "days": days})


@login_required(login_url="/", redirect_field_name=None)
def projects(request):
    projects = Project.by_total_duration(request.user)
    return render(request, "projects.html", {"projects": projects})


@login_required(login_url="/", redirect_field_name=None)
def edit_session(request, pk):
    try:
        session = Session.objects.get(id=pk, project__user=request.user)
    except Session.DoesNotExist:
        raise Http404
    form = SessionForm(instance=session)
    if request.method == "POST":
        form = process_session_form_data(request, instance=session)
        if form.is_valid():
            form.save(request.user)
            return redirect(form.instance.local_start().strftime("/time/%Y/%m/%d/"))
    return render(request, "edit-session.html", {"form": form})


@login_required(login_url="/", redirect_field_name=None)
def delete_session(request, pk):
    try:
        session = Session.objects.get(id=pk, project__user=request.user)
    except Session.DoesNotExist:
        raise Http404
    if request.method == "POST":
        session.delete()
        return redirect("/time/{}/{}/{}/".format(session.local_start().year, session.local_start().month, session.local_start().day))
    return render(request, "delete-session.html", {"session": session})


@login_required(login_url="/", redirect_field_name=None)
def time_day(request, year, month, day):
    form = SessionForm(date=date(year, month, day))
    if request.method == "POST":
        form = process_session_form_data(request, date=date(year, month, day))
        if form.is_valid():
            form.save(request.user)
            return redirect("/time/{}/{}/{}/".format(year, month, day))
    day = Session.from_day(request.user, date(year, month, day))
    return render(request, "time-tracking-day.html", {"day": day, "form": form})
