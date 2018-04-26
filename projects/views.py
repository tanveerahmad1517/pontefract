from datetime import date, timedelta
from calendar import monthrange
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.forms import SignupForm, LoginForm
from projects.forms import SessionForm, ProjectForm
from projects.models import Session, Project





@login_required(login_url="/", redirect_field_name=None)
def time_month(request, year, month):
    month_date, first_month = date(year, month, 1), request.user.first_month()
    if not first_month or month_date < first_month:
        raise Http404
    today = request.now.date()
    days = Session.group_by_date(request.user, month=date(year, month, 1))
    next = date(
     year + 1 if month == 12 else year, 1 if month == 12 else month + 1, 1
    )
    if next > today: next = None
    previous = date(
     year - 1 if month == 1 else year, 12 if month == 1 else month - 1, 1
    )
    if previous < request.user.first_month(): previous = None
    return render(request, "time-tracking-month.html", {
     "month": date(year, month, 1),
     "days": days,
     "next": next,
     "previous": previous
    })


@login_required(login_url="/", redirect_field_name=None)
def time_projects(request, pk):
    try:
        project = Project.objects.get(id=pk, user=request.user)
    except Project.DoesNotExist: raise Http404
    days = Session.group_by_date(request.user, project=project)
    return render(request, "project.html", {"project": project, "days": days})


@login_required(login_url="/", redirect_field_name=None)
def projects(request):
    return render(request, "projects.html")


@login_required(login_url="/", redirect_field_name=None)
def edit_session(request, pk):
    try:
        session = Session.objects.get(id=pk, project__user=request.user)
    except Session.DoesNotExist:
        raise Http404
    form = SessionForm(instance=session)
    if request.method == "POST":
        try:
            ProjectForm(request.user, request.POST).save()
        except: pass
        form = SessionForm(request.POST, user=request.user, instance=session)
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
    from django.utils import timezone
    form = SessionForm(date=date(year, month, day))
    if request.method == "POST":
        try:
            ProjectForm(request.user, request.POST).save()
        except: pass
        form = SessionForm(request.POST, user=request.user, date=date(year, month, day))
        if form.is_valid():
            form.save(request.user)
            return redirect("/time/{}/{}/{}/".format(year, month, day))
    day = Session.from_day(request.user, date(year, month, day))
    yesterday = day[0] - timedelta(days=1)
    tomorrow = day[0] + timedelta(days=1)
    return render(request, "time-tracking-day.html", {"day": day, "form": form, "yesterday": yesterday, "tomorrow": tomorrow})
