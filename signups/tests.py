from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta

from .models import VolunteerForm, VolunteerSlot


class CSRFProtectionTests(TestCase):
    """Test that CSRF protection is properly enforced on POST endpoints"""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.volunteer_form = VolunteerForm.objects.create(
            title='Test Form',
            description='Test Description',
            created_by=self.user,
            is_active=True
        )
        self.slot = VolunteerSlot.objects.create(
            form=self.volunteer_form,
            title='Test Slot',
            date=date.today() + timedelta(days=7),
            max_volunteers=5,
            current_signups=0
        )
    
    def test_post_without_csrf_token_fails(self):
        """Test that POST requests without CSRF token are rejected"""
        url = reverse('signups:slot_detail', kwargs={
            'unique_url': self.volunteer_form.unique_url,
            'slot_id': self.slot.id
        })
        
        # Attempt POST without CSRF token
        response = self.client.post(url, {
            'name': 'Test User',
            'email': 'test@example.com'
        })
        
        # Should be rejected with 403 Forbidden
        self.assertEqual(response.status_code, 403)
        # Verify no signup was created
        self.assertEqual(self.slot.signups.count(), 0)
    
    def test_post_with_csrf_token_succeeds(self):
        """Test that POST requests with CSRF token succeed"""
        url = reverse('signups:slot_detail', kwargs={
            'unique_url': self.volunteer_form.unique_url,
            'slot_id': self.slot.id
        })
        
        # First, get the page to obtain CSRF token
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        
        # Get CSRF token from cookie
        csrf_token = self.client.cookies.get('csrftoken')
        self.assertIsNotNone(csrf_token, "CSRF token should be available in cookie")
        
        # Make POST request with CSRF token
        response = self.client.post(url, {
            'name': 'Test User',
            'email': 'test@example.com',
            'csrfmiddlewaretoken': csrf_token.value
        })
        
        # Should redirect on success (status 302)
        self.assertEqual(response.status_code, 302)
        
        # Verify signup was created
        self.slot.refresh_from_db()
        self.assertEqual(self.slot.signups.count(), 1)
        signup = self.slot.signups.first()
        self.assertEqual(signup.name, 'Test User')
        self.assertEqual(signup.email, 'test@example.com')
        # Verify current_signups was incremented
        self.assertEqual(self.slot.current_signups, 1)


class SecretKeySecurityTests(TestCase):
    """Test that SECRET_KEY security logic works correctly"""
    
    def test_secret_key_logic_imports_correctly(self):
        """Test that settings module imports without error when SECRET_KEY is set"""
        # This test verifies that the SECRET_KEY logic doesn't break imports
        # In a real test environment, SECRET_KEY should be set
        from django.conf import settings
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertIsInstance(settings.SECRET_KEY, str)
        self.assertGreater(len(settings.SECRET_KEY), 0)
    
    def test_secret_key_not_insecure_fallback(self):
        """Test that SECRET_KEY is not the insecure hardcoded fallback"""
        from django.conf import settings
        insecure_fallback = 'django-insecure-!n1$_i=*na4e-&ti8zsq^lg628u+8ho5z=+^1^(06y%478-^+!'
        self.assertNotEqual(
            settings.SECRET_KEY,
            insecure_fallback,
            "SECRET_KEY should not be the insecure hardcoded fallback"
        )
