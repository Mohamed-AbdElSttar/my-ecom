from django.urls import path
from .views import CustomLoginView, register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('password-reset/', password_reset_request, name='password_reset'),
]