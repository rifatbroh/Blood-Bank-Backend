from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField
from events.models import DonationEvent


class DonorRegistrationModel(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE)
     age=models.PositiveIntegerField()
     mobaile_no=models.PositiveIntegerField()
     address=models.TextField()
     



# # Create your models here.

class DonorProfile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)
    
     age = models.PositiveIntegerField()
     image = models.ImageField(upload_to="accounts/media/images")

     # image=models.ImageField(upload_to="images")
     address = models.TextField()
     mobaile_no = models.PositiveIntegerField()
     blood_group = models.CharField(max_length=3)
     is_available = models.BooleanField(default=True)
     health_screening_passed = models.BooleanField(default=False)


     
     def __str__(self):
          return self.user.username