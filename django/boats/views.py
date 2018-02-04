from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView, DetailView, ListView

from api.models import Boat


class BoatView(DetailView):
    model = Boat
    template_name = 'boat.html'
    context_object_name = 'boat'


class BoatListView(ListView):
    model = Boat
    context_object_name = 'boats'
    template_name = 'boat_list.html'


class NewBoatView(CreateView):
    model = Boat
    fields = ['name']
    template_name = 'new_boat.html'

    def form_valid(self, form):
        form.instance.manager = self.request.user
        return super().form_valid(form)


class UsersBoatsView(ListView):
    """List of boats for a user"""
    model = Boat
    template_name = 'users_boats.html'
    context_object_name = 'boats'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Lookup url supplied user, process get request"""
        users = get_user_model()
        self.user = users.objects.get(username=self.kwargs.get('username'))
        return super(UsersBoatsView, self).get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        boats = Boat.objects.filter(manager__username=self.user)
        return boats
