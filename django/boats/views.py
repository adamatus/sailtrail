from django.views.generic import CreateView, DetailView, ListView, View

from api.models import Boat


class BoatView(DetailView):
    model = Boat
    template_name = 'boat.html'
    context_object_name = 'boat'


class BoatListView(View):
    pass


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
