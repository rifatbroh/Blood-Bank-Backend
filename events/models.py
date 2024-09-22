from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .constraints import EVENT_STATUS_CHOICES

from django.contrib.auth.models import User

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    blood_group = models.CharField(max_length=10, choices=[(bg, bg) for bg in ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')])
    location = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification from {self.sender} to {self.recipient} for {self.blood_group} blood"





class DonationEvent(models.Model):
    
    event_name = models.CharField(max_length=255)
    recipient = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=10, choices=[(bg, bg) for bg in ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')])
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    status = models.CharField(max_length=10, choices=EVENT_STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.event_name} - {self.recipient}"



class DonationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donation_history")
    event = models.ForeignKey(DonationEvent, on_delete=models.CASCADE)
    accepted_on = models.DateTimeField(auto_now_add=True)
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"Donation by {self.user.username} for {self.event.event_name}"




