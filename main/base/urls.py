from django.urls import path
from . import views
from .views import (TaskList, TaskDetail, TaskCreate, TaskUpdate,
                    TaskDelete, CustomLoginView, RegisterPage,
                    UserSearchView, UserProfileView, UserListView, add_friend, friend_list,
                    remove_friend)

from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),

    path('', TaskList.as_view(), name='task'),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task'),
    path('task-create/', TaskCreate.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdate.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', TaskDelete.as_view(), name='task-delete'),
    path('search-users/', UserSearchView.as_view(), name='search-users'),
    path('search-users/', UserListView.as_view(), name='search-users'),
    path('user/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('user-profile/<str:username>/', UserProfileView.as_view(), name='user-profile'),

    path('add_friend/<str:username>/', add_friend, name='add_friend'),
    path('friends/', friend_list, name='friend_list'),
    path('remove-friend/<str:username>/', remove_friend, name='remove-friend'),

]