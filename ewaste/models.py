from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EWasteCategory(models.Model):
    """Categories of e-waste items"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='📱')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "E-Waste Categories"


class EWasteItem(models.Model):
    """Individual e-waste items reported by users"""
    CONDITION_CHOICES = [
        ('working', 'Working'),
        ('partial', 'Partially Working'),
        ('broken', 'Broken'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ewaste_items')
    category = models.ForeignKey(EWasteCategory, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=200)
    description = models.TextField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    quantity = models.IntegerField(default=1)
    pickup_location = models.CharField(max_length=500)
    preferred_date = models.DateField()
    contact_phone = models.CharField(max_length=15)
    images = models.TextField(blank=True, help_text="Store image paths or URLs")
    is_collected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.item_name} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']


class PickupRequest(models.Model):
    """Tracks pickup requests for e-waste items"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    ewaste_item = models.OneToOneField(EWasteItem, on_delete=models.CASCADE, related_name='pickup_request')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pickup - {self.ewaste_item.item_name} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']


class RecyclingFacility(models.Model):
    """Information about recycling facilities"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    accepted_items = models.TextField(help_text="Comma-separated list of accepted items")
    operating_hours = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Recycling Facilities"


class Feedback(models.Model):
    """User feedback about the platform"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.user.username} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


class Company(models.Model):
    """Represents a partner company / company admin contact"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Extended profile for users to handle company/customer role"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_company = models.BooleanField(default=False)
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Notification(models.Model):
    """In-app notification for staff/company users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.message[:75] + '...') if len(self.message) > 75 else self.message

    class Meta:
        ordering = ['-created_at']
