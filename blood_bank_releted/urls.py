from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AboutUsViewSet, ContactViewSet,  FeedbackViewSet,BlogPostViewSet,All_Feddback
# BlogPostViewSet,

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'about-us', AboutUsViewSet, basename='about-us')
router.register(r'contact', ContactViewSet, basename='contact')
router.register(r'blog', BlogPostViewSet, basename='blog')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'all_feedback', All_Feddback, basename='all_feedback')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),


]
