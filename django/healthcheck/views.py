import traceback

from django.http import HttpResponse, HttpResponseServerError
from django.views.generic import View

from healthcheck.models import Healthcheck


def check_db():
    """Do a basic sanity check on the DB"""
    Healthcheck.objects.create(source='DB')


class HealthcheckView(View):
    """Healhcheck view"""

    def get(self, request):
        """Get request for healthcheck

        The existence of this response verifies the service is up.
        Also checks that the DB is responding.
        """

        ok = True
        status = []

        try:
            check_db()
            status.append('DB: OK')
        except:
            ok = False
            error_msg = 'DB: BAD ({})'.format(traceback.format_exc())
            status.append(error_msg)

        response = HttpResponse if ok else HttpResponseServerError
        return response("\n".join(status), content_type="text/plain")
