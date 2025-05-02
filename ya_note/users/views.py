from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def user_logout(request):
    logout(request)
    return render(request, 'registration/logout.html')
