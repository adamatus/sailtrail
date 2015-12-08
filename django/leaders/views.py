"""Activity view module"""
from django.views.generic import TemplateView

from api.models import get_leaders
from core.views import UploadFormMixin


class LeaderboardView(UploadFormMixin, TemplateView):
    """Leaderboard view"""
    template_name = 'leaderboards.html'

    def get_context_data(self, **kwargs):
        """Update the context with leaders"""
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        context['leaders'] = get_leaders()
        return context
