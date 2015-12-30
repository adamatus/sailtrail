"""Activity view module"""
from django.views.generic import TemplateView

from api.models import Helper
from core.views import UploadFormMixin


class LeaderboardView(UploadFormMixin, TemplateView):
    """Leaderboard view"""
    template_name = 'leaderboards.html'

    def get_context_data(self, **kwargs) -> dict:
        """Update the context with leaders"""
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        context['leaders'] = Helper.get_leaders()
        return context
