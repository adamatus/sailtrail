"""Activity view module"""
from allauth.account.views import PasswordChangeView
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView

from api.models import Helper
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

        activities = Helper.get_users_activities(self.object,
                                                 self.request.user)
        context['activities'] = activities
        context['summaries'] = Helper.summarize_by_category(activities)

        return context


class UserSettingsView(UploadFormMixin, DetailView):
    """User settings page view"""
    model = get_user_model()
    slug_field = 'username'
    template_name = 'user_settings.html'
    context_object_name = 'view_user'

    def get_context_data(self, **kwargs):
        """Add additional content to the user page"""
        context = super(UserSettingsView, self).get_context_data(**kwargs)

        notify = self.request.session.get('notify', None)
        if notify is not None:
            context['notify'] = notify
            del self.request.session['notify']

        return context


class ChangePasswordView(PasswordChangeView):
    """Change password view"""

    def get_success_url(self):
        """Get a success url, for the current user"""
        self.request.session['notify'] = 'Password successfully updated'
        return reverse('user_settings', args=[self.request.user.username])


class UserListView(UploadFormMixin, ListView):
    """List of all users"""
    model = get_user_model()
    template_name = 'user_list.html'
    context_object_name = 'users'
