from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm
from django.views.generic import CreateView
from django.urls import reverse_lazy

# Create your views here.

def register(request):
    """
    View function for user registration
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-login after registration
            login(request, user)
            
            # Success message
            messages.success(
                request, 
                f'Account created successfully! Welcome, {user.username}.'
            )
            
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

