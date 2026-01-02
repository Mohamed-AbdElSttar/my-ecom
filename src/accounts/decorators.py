from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.conf import settings

def rate_limit(max_attempts=5, timeout=300):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # CRITICAL FIX: Check TESTING setting properly
            if hasattr(settings, 'TESTING') and settings.TESTING:
                return view_func(request, *args, **kwargs)
            
            # Only rate limit POST requests to login
            if request.method != 'POST':
                return view_func(request, *args, **kwargs)
            
            # Get IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                return HttpResponseForbidden("Too many login attempts.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def increment_login_attempts(request):
    """Increment login attempts counter for failed login"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    cache_key = f'login_attempts_{ip}'
    attempts = cache.get(cache_key, 0)
    cache.set(cache_key, attempts + 1, 300)  # 5 minutes timeout