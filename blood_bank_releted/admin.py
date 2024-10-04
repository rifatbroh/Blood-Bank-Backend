from django.contrib import admin
from .models import AboutUs,Contact,Feedback,DonorBlogPost
admin.site.register(DonorBlogPost)
admin.site.register(Contact)
admin.site.register(Feedback)
admin.site.register(AboutUs)
# Register your models here.
