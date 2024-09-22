from django.contrib import admin
from .models import DonorRegistrationModel,DonorProfile
# Register your models here.
admin.site.register(DonorProfile)
admin.site.register(DonorRegistrationModel)