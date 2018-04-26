class TimeTrackingMonthViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.request.user.sessions_today.side_effect = lambda d: d.day
        self.request.user.hours_worked_today.side_effect = lambda d: d.day * 2
        self.request.user.first_month.return_value = date(1983, 6, 1)
        self.request.now = datetime(1984, 10, 3)
        self.patch1 = patch("core.views.Session.group_by_date")
        self.mock_group = self.patch1.start()
        self.mock_group.return_value = [1, 2, 3]


    def tearDown(self):
        self.patch1.stop()


    def test_month_view_uses_month_template(self):
        self.check_view_uses_template(
         time_month, self.request, "time-month.html", 1990, 10
        )


    def test_month_view_sends_date(self):
        self.check_view_has_context(
         time_month, self.request, {"month": date(1990, 10, 1)}, 1990, 10
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_days(self):
        self.check_view_has_context(
         time_month, self.request, {"days": [1, 2, 3]}, 1984, 10
        )
        self.mock_group.assert_called_with(self.request.user, month=date(1984, 10, 1))


    @freeze_time("1984-10-3")
    def test_month_view_sends_next_month(self):
        self.check_view_has_context(time_month, self.request, {"next": None}, 1984, 10)
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 10, 1)}, 1984, 9
        )
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 2, 1)}, 1984, 1
        )
        self.check_view_has_context(
         time_month, self.request, {"next": date(1984, 1, 1)}, 1983, 12
        )


    @freeze_time("1984-10-3")
    def test_month_view_sends_previous_month(self):
        self.check_view_has_context(
         time_month, self.request, {"previous": date(1984, 9, 1)}, 1984, 10
        )
        self.check_view_has_context(
         time_month, self.request, {"previous": date(1983, 12, 1)}, 1984, 1
        )
        self.check_view_has_context(
         time_month, self.request, {"previous": None}, 1983, 6
        )


    def test_month_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(time_month, request, "/", 1962, 4)


    def test_month_view_raises_404_on_month_out_of_bounds(self):
        with self.assertRaises(Http404):
            time_month(self.request, 1961, 6)


    def test_month_view_raises_404_on_no_sessions(self):
        self.request.user.first_month.return_value = None
        with self.assertRaises(Http404):
            time_month(self.request, 1984, 4)



class TimeTrackingProjectViewTests(DjangoTest):

    def setUp(self):
        self.request = self.make_request("---", loggedin=True)
        self.patch1 = patch("core.views.Project.objects.get")
        self.mock_get = self.patch1.start()
        self.mock_get.return_value = "PROJECT"
        self.patch2 = patch("core.views.Session.group_by_date")
        self.mock_group = self.patch2.start()
        self.mock_group.return_value = [1, 2, 3]


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_project_view_uses_project_template(self):
        self.check_view_uses_template(
         time_projects, self.request, "time-projects.html", 3
        )


    def test_project_view_sends_project(self):
        self.check_view_has_context(
         time_projects, self.request, {"project": "PROJECT"}, 3
        )
        self.mock_get.assert_called_with(id=3, user=self.request.user)


    def test_project_view_sends_days(self):
        self.check_view_has_context(
         time_projects, self.request, {"days": [1, 2, 3]}, 3
        )
        self.mock_group.assert_called_with(self.request.user, project="PROJECT")


    def test_project_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(time_projects, request, "/", 3)


    def test_project_view_raises_404_on_non_project(self):
        self.mock_get.side_effect = Project.DoesNotExist
        with self.assertRaises(Http404):
            time_projects(self.request, 3)



class ProjectsViewTests(DjangoTest):

    def test_projects_view_uses_projects_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(projects, request, "projects.html")


    def test_projects_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(projects, request, "/")



class EditSessionViewTests(DjangoTest):

    def setUp(self):
        self.patch1 = patch("core.views.Session.objects.get")
        self.mock_get = self.patch1.start()
        self.mock_get.return_value = "SESSION"
        self.patch2 = patch("core.views.SessionForm")
        self.mock_form = self.patch2.start()
        self.mock_form.return_value = "FORM"


    def tearDown(self):
        self.patch1.stop()
        self.patch2.stop()


    def test_edit_session_view_uses_right_template(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_uses_template(edit_session, request, "edit-session.html", 10)


    def test_session_edit_view_requires_auth(self):
        request = self.make_request("---")
        self.check_view_redirects(edit_session, request, "/", 10)


    def test_session_edit_view_404(self):
        request = self.make_request("---", loggedin=True)
        self.mock_get.side_effect = Session.DoesNotExist
        with self.assertRaises(Http404):
            edit_session(request, 10)
        self.mock_get.assert_called_with(id=10, project__user=request.user)


    def test_edit_session_view_sends_bound_form(self):
        request = self.make_request("---", loggedin=True)
        self.check_view_has_context(
         edit_session, request, {"form": "FORM"}, 10
        )
        self.mock_form.assert_called_with(instance="SESSION")
