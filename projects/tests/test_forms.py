from unittest.mock import patch
from testarsenal import DjangoTest
from projects.forms import *

class SessionFormTests(DjangoTest):

    def test_session_form_has_correct_fields(self):
        form = SessionForm()
        self.assertEqual(
         list(form.fields.keys()), ["start", "end", "breaks", "project"]
        )
