from django.urls import path
from .views import user_logout


app_name = 'users'

urlpatterns = [
    path('logout/', user_logout, name='logout'),
]
