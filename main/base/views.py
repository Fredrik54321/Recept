
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
import random

from .models import Task, Friendship


from django.contrib.auth.views import  LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User






class UserSearchView(ListView):
    model = User
    template_name = 'search_users.html'
    context_object_name = 'users'

    def get_queryset(self):
        search_input = self.request.GET.get('Sök-ruta', '')
        if search_input:
            return User.objects.filter(username__icontains=search_input)
        return User.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_input'] = self.request.GET.get('Sök-ruta', '')
        return context



class UserProfileView(DetailView):
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):

        username = self.kwargs.get('username')  # Hämta användarnamnet från URL
        return User.objects.get(username=username)  # Hämta användaren med det användarnamnet

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.get_object()  # Användaren som vi just hämtade
        context['tasks'] = Task.objects.filter(user=user)  # Om du vill visa användarens uppgifter

        user_profile = getattr(user, 'userprofile', None)

        context[
            'profile_picture'] = user_profile.profile_picture.url if user_profile and user_profile.profile_picture else '/media/profile_pics/default.jpg'
        context['tasks'] = Task.objects.filter(user=user)

        return context



class UserListView(ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()  # Hämta alla användare
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('task')

class RegisterPage(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('task')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin ,ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(completed=False).count()

        search_input = self.request.GET.get('Sök-ruta') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)

        context ['search_input'] = search_input

        context['random_task'] = random.choice(context['tasks']) if context['tasks'].exists() else None

        return context

class TaskDetail(LoginRequiredMixin ,DetailView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['profile_url'] = reverse_lazy('user-profile', kwargs={'username': task.user.username})
        return context


class TaskCreate(LoginRequiredMixin ,CreateView):
    model = Task
    fields = ['title', 'description']
    success_url = '/'
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdate(LoginRequiredMixin ,UpdateView):
    model = Task
    fields = ['title', 'description']
    success_url = '/'
    template_name = 'task_form.html'

class TaskDelete(LoginRequiredMixin ,DeleteView):
    model = Task
    context_object_name = 'tasks'
    success_url = '/'
    template_name = 'task_delete.html'



@login_required
def add_friend(request, username):
    friend = get_object_or_404(User, username=username)
    Friendship.objects.get_or_create(user=request.user, friend=friend)
    Friendship.objects.get_or_create(user=friend, friend=request.user)  # Tvåvägs vänskap
    return redirect('friend_list')

@login_required
def friend_list(request):
    friends = Friendship.objects.filter(user=request.user).select_related('friend')
    return render(request, 'friend_list.html', {'friends': friends})

def remove_friend(request, username):
    # Hämta den inloggade användaren och vännen med användarnamnet
    user = request.user
    friend = get_object_or_404(User, username=username)


    # Försök att ta bort vänskapsrelationen mellan de två användarna
    try:
        friendship = Friendship.objects.get(user=user, friend=friend)
        friendship.delete()
        messages.success(request, f"{friend.username} har tagits bort som vän.")
    except Friendship.DoesNotExist:
        pass  # Om vänskapen inte finns, gör inget (eller hantera felet om så önskas)

    # Efter borttagning omdirigera till vänlistan
    return redirect('friend_list')  # Detta omdirigerar till vänlistan

