from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
import uuid

class VolunteerType(models.Model):
    """Predefined volunteer task types with descriptions"""
    name = models.CharField(max_length=200, help_text="Name of the volunteer task type")
    description = models.TextField(help_text="Standard description for this type of volunteer task")
    is_active = models.BooleanField(default=True, help_text="Whether this volunteer type is available for use")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class VolunteerForm(models.Model):
    """A volunteer form that contains multiple volunteer slots"""
    title = models.CharField(max_length=200, help_text="Title of the volunteer form")
    description = models.TextField(help_text="Description of the volunteer opportunity")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether this form is currently accepting signups")
    unique_url = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique URL identifier for this form")
    
    def save(self, *args, **kwargs):
        if not self.unique_url:
            # Generate a unique URL using a combination of slugified title and UUID
            base_slug = slugify(self.title)[:20]  # Limit to 20 chars
            unique_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
            self.unique_url = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_form_url(self):
        """Generate the full URL for this volunteer form"""
        return reverse('signups:volunteer_form_view', kwargs={'unique_url': self.unique_url})
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class VolunteerSlot(models.Model):
    """Individual volunteer slots within a form"""
    form = models.ForeignKey(VolunteerForm, on_delete=models.CASCADE, related_name='slots')
    volunteer_type = models.ForeignKey(VolunteerType, on_delete=models.SET_NULL, null=True, blank=True, help_text="Type of volunteer task (optional)")
    title = models.CharField(max_length=200, help_text="Title of this volunteer slot")
    description = models.TextField(blank=True, help_text="Description of what this slot involves")
    date = models.DateField(help_text="Date when this volunteer slot occurs")
    max_volunteers = models.PositiveIntegerField(default=1, help_text="Maximum number of volunteers for this slot")
    current_signups = models.PositiveIntegerField(default=0, help_text="Current number of signups")
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    def is_full(self):
        return self.current_signups >= self.max_volunteers
    
    def available_spots(self):
        return max(0, self.max_volunteers - self.current_signups)
    
    class Meta:
        ordering = ['date']

class VolunteerSignup(models.Model):
    """Individual volunteer signups for slots"""
    slot = models.ForeignKey(VolunteerSlot, on_delete=models.CASCADE, related_name='signups')
    name = models.CharField(max_length=100, help_text="Name of the volunteer")
    email = models.EmailField(help_text="Email address of the volunteer")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number (optional)")
    notes = models.TextField(blank=True, help_text="Any additional notes from the volunteer")
    signed_up_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.slot.title}"
    
    def save(self, *args, **kwargs):
        # Update the current_signups count when a signup is created
        if not self.pk:  # Only on creation
            self.slot.current_signups += 1
            self.slot.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Update the current_signups count when a signup is deleted
        self.slot.current_signups -= 1
        self.slot.save()
        super().delete(*args, **kwargs)
    
    class Meta:
        ordering = ['signed_up_at']
