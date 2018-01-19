"""Activity view module"""
from allauth.account.views import PasswordChangeView
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView

from api.helper import get_users_activities, summarize_by_category
from api.models import Activity
from core.views import UploadFormMixin


class UserView(UploadFormMixin, ListView):
    """Individual user page view"""
    model = Activity
    template_name = 'user.html'
    context_object_name = 'activities'
    paginate_by = 25
    user = None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Lookup url supplied user, process get request"""
        users = get_user_model()
        self.user = users.objects.get(username=self.kwargs.get('username'))
        return super(UserView, self).get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        """Return the users activities, include private if current user"""
        return get_users_activities(self.user,
                                    self.request.user)

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(UserView, self).get_context_data(**kwargs)
        context['view_user'] = self.user
        context['summaries'] = summarize_by_category(
            self.get_queryset())
        return context


class UserSettingsView(UploadFormMixin, DetailView):
    """User settings page view"""
    model = get_user_model()
    slug_field = 'username'
    template_name = 'user_settings.html'
    context_object_name = 'view_user'

    def get_context_data(self, **kwargs) -> dict:
        """Add additional content to the user page"""
        context = super(UserSettingsView, self).get_context_data(**kwargs)

        notify = self.request.session.get('notify', None)
        if notify is not None:
            context['notify'] = notify
            del self.request.session['notify']

        return context


class ChangePasswordView(PasswordChangeView):
    """Change password view"""

    def get_success_url(self) -> str:
        """Get a success url, for the current user"""
        self.request.session['notify'] = 'Password successfully updated'
        return reverse('users:user_settings',
                       args=[self.request.user.username])


class UserListView(UploadFormMixin, ListView):
    """List of all users"""
    model = get_user_model()
    template_name = 'user_list.html'
    context_object_name = 'users'
