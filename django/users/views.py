"""Activity view module"""
from django.contrib.auth import get_user_model
from django.views.generic import ListView, DetailView

from api.models import get_users_activities, summarize_by_category
from core.views import UploadFormMixin


class UserView(UploadFormMixin, DetailView):
    """Individual user page view"""
    model = get_user_model()
    slug_field = 'username'
    template_name = 'user.html'
    context_object_name = 'view_user'

    def get_context_data(self, **kwargs):
        """Add additional content to the user page"""
        context = super(UserView, self).get_context_data(**kwargs)

        activities = get_users_activities(self.object,
                                          self.request.user)
        context['activities'] = activities
        context['summaries'] = summarize_by_category(activities)

        return context


class UserListView(UploadFormMixin, ListView):
    """List of all users"""
    model = get_user_model()
    template_name = 'user_list.html'
    context_object_name = 'users'
