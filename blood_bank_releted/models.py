
from django.db import models
from django.contrib.auth.models import User
from events.models import DonationEvent
# Create your models here.
from .constraints import STAR_CHOICES,EVENT_CHOICES
from cloudinary.models import CloudinaryField
class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    mission = models.TextField()
    vision = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DonorBlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author= models.ForeignKey(User,on_delete=models.CASCADE, related_name='blogreleted')  # Donor info
    image = models.ImageField(upload_to="blood_bank_releted/media/images")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Feedback(models.Model):
    donor = models.ForeignKey(User,on_delete=models.CASCADE, related_name='feedbacks')  # Donor info

    rating = models.CharField(max_length=7, choices=STAR_CHOICES, default='⭐')  # Rating field (1 to 5 stars)
    feedback = models.TextField()  # Feedback details from donor
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for feedback creation

    def __str__(self):
        return f'Feedback by {self.donor.username}'
