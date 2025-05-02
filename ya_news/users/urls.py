# users/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import register, user_logout

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('signup/', register, name='signup'),
]
