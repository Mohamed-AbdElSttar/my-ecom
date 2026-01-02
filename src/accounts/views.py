from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm, LoginForm
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .decorators import rate_limit, increment_login_attempts



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



class CustomLoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    @method_decorator(rate_limit(max_attempts=5, timeout=300))
    @method_decorator(csrf_protect)
    @method_decorator(require_http_methods(["GET", "POST"]))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # If user is already logged in, redirect to homepage
        if request.user.is_authenticated:
            return redirect('home')
        
        form = self.form_class()
        next_url = request.GET.get('next', '')
        return render(request, self.template_name, {
            'form': form,
            'next': next_url
        })
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request, data=request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Login the user
            login(request, user)
            
            # Set session expiry based on "Remember me"
            if remember_me:
                # 30 days persistence
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days in seconds
            else:
                # 24 hours inactivity timeout
                request.session.set_expiry(60 * 60 * 24)  # 24 hours in seconds
                request.session.setdefault('session_expiry', 60 * 60 * 24)
            
            # Handle redirect
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            
            # Default redirect to homepage
            return redirect('home')
        else:
            # Increment failed login attempts
            increment_login_attempts(request)
        
        # If form is invalid, show errors
        return render(request, self.template_name, {
            'form': form,
            'next': request.POST.get('next', '')
        })


@login_required
def profile_view(request):
    """Simple profile view for testing redirects"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })