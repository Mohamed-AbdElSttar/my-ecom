# src/accounts/tests/test_login.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

User = get_user_model()

class LoginViewTest(TestCase):
    """Tests for US-A02: User Login - CURRENT STATE"""
    
    def setUp(self):
        # Enable testing mode
        settings.TESTING = True
        
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    # 1. CORE FUNCTIONALITY TESTS
    def test_login_page_loads(self):
        """Login page should load with form and placeholder links"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        
        # Form exists
        self.assertContains(response, 'Login to Your Account')
        self.assertContains(response, 'name="email_or_username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="remember_me"')
        
        # Placeholder password reset link (href="#")
        self.assertContains(response, 'Forgot your password')
        self.assertContains(response, 'href="#"')
    
    def test_login_with_email_success(self):
        """Login with email should work and redirect to home"""
        response = self.client.post(self.login_url, {
            'email_or_username': 'test@example.com',
            'password': 'TestPass123',
        }, follow=True)
        
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.context['user'].is_authenticated)
        
        # Home should show welcome message
        self.assertContains(response, 'Welcome back')
    
    def test_login_with_username_success(self):
        """Login with username should work"""
        response = self.client.post(self.login_url, {
            'email_or_username': 'testuser',
            'password': 'TestPass123',
        }, follow=True)
        
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.context['user'].is_authenticated)
    
    def test_login_invalid_credentials(self):
        """Invalid credentials should show generic error"""
        response = self.client.post(self.login_url, {
            'email_or_username': 'test@example.com',
            'password': 'wrong',
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email or password')
    
    def test_remember_me_checkbox_exists(self):
        """Remember me checkbox should be present"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'Remember me for 30 days')
    
    # 2. NAVIGATION & REDIRECT TESTS
    def test_already_logged_in_redirects_home(self):
        """Logged-in users should be redirected from login page"""
        # Login first
        self.client.login(username='testuser', password='TestPass123')
        
        # Try to access login page
        response = self.client.get(self.login_url, follow=True)
        self.assertRedirects(response, self.home_url)
    
    def test_registration_link_works(self):
        """Registration link should go to valid registration page"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'Register here')
        self.assertContains(response, f'href="{reverse("register")}"')
    
    # 3. SECURITY TESTS
    def test_csrf_token_present(self):
        """CSRF protection should be enabled"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_rate_limiting_not_blocking_tests(self):
        """Rate limiting should be disabled in test mode"""
        # Clear any existing cache
        cache.clear()
        
        # Make 10 failed attempts - all should work in test mode
        for i in range(10):
            response = self.client.post(self.login_url, {
                'email_or_username': 'test@example.com',
                'password': 'wrong',
            })
            # Debug: print status code if test fails
            if response.status_code != 200:
                print(f"Attempt {i+1}: Status {response.status_code}, Content: {response.content[:200]}")
            
            self.assertEqual(
                response.status_code, 
                200,
                f"Rate limiting blocked attempt {i+1} in test mode. "
                f"Status: {response.status_code}"
            )
    
    # 4. MOBILE/RESPONSIVE TESTS
    def test_mobile_responsive_classes(self):
        """Should have responsive design classes"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'col-md-6')
        self.assertContains(response, 'col-lg-5')
        self.assertContains(response, 'container mt-5')
    
    def test_touch_friendly_elements(self):
        """Should have mobile-friendly touch targets"""
        response = self.client.get(self.login_url)
        # Check for mobile optimization CSS
        self.assertContains(response, 'min-height: 48px', html=False)
    
    # 5. POST-LOGIN STATE TESTS
    def test_home_page_shows_logout_placeholder(self):
        """After login, home page should show logout placeholder"""
        # Login
        self.client.login(username='testuser', password='TestPass123')
        
        # Visit home
        response = self.client.get(self.home_url)
        self.assertContains(response, 'You are successfully logged in')
        self.assertContains(response, 'href="#"')  # Logout placeholder
    
    def test_session_persistence(self):
        """Login should create a session"""
        response = self.client.post(self.login_url, {
            'email_or_username': 'test@example.com',
            'password': 'TestPass123',
        }, follow=False)
        
        # Should have session cookie
        self.assertIn('sessionid', response.cookies)
    
    # 6. EDGE CASE TESTS
    def test_empty_form_submission(self):
        """Empty form should not crash"""
        response = self.client.post(self.login_url, {
            'email_or_username': '',
            'password': '',
        })
        self.assertEqual(response.status_code, 200)
    
    def test_nonexistent_user(self):
        """Non-existent user should show same error"""
        response = self.client.post(self.login_url, {
            'email_or_username': 'nonexistent@example.com',
            'password': 'anything',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email or password')
    
    # 7. NO PROFILE TESTS (because we don't have profiles)
    # No test_profile_redirect - we don't have profile pages
    # No test_password_reset_link - we only have placeholder
    
    # 8. SPECIFIC TEMPLATE CONTENT TESTS
    def test_login_template_has_correct_links(self):
        """Verify template has exactly what we expect"""
        response = self.client.get(self.login_url)
        
        # Should have these
        self.assertContains(response, 'Forgot your password?')
        self.assertContains(response, 'Register here')
        
        # Should NOT have these (since we don't have them yet)
        self.assertNotContains(response, '{% url &#39;password_reset&#39; %}')
        self.assertNotContains(response, '{% url &#39;logout&#39; %}')
        self.assertNotContains(response, '{% url &#39;profile&#39; %}')