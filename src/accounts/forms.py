from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class UserRegisterForm(UserCreationForm):
    """
    Custom registration form that extends Django's UserCreationForm
    Adds email, first_name, last_name fields and custom validation
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

        def clean_email(self):
            """
            Validate that email is unique
            """
            email = self.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                raise ValidationError("This email address is already registered.")
            return email
        
        def clean_username(self):
            """
            Validate username uniqueness
            """
            username = self.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                raise ValidationError("This username is already taken.")
            return username
        


class LoginForm(AuthenticationForm):
    email_or_username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email or username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Remember me for 30 days",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default username field
        self.fields.pop('username', None)
    
    def clean(self):
        email_or_username = self.cleaned_data.get('email_or_username')
        password = self.cleaned_data.get('password')
        
        if email_or_username and password:
            # Try to authenticate with both email and username
            user = None
            
            # First try email
            try:
                user_obj = User.objects.get(email=email_or_username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
            
            # If not found by email, try username
            if user is None:
                user = authenticate(username=email_or_username, password=password)
            
            if user is None:
                raise ValidationError(
                    "Email or password isn't correct",
                    code='invalid_login'
                )
            
            # Check if user is active
            if not user.is_active:
                raise ValidationError(
                    "This account is inactive.",
                    code='inactive'
                )
            
            self.cleaned_data['user'] = user
            
        return self.cleaned_data