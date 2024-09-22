from rest_framework.routers import DefaultRouter
from django.urls import path,include

from .views import UserRegistrationView,UserLoginView,UserLogoutView,activate,DonorProfileView

router = DefaultRouter()
router.register('profile',DonorProfileView, basename='profile')

# router.register()
urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('active/<uid>/<token>/',activate, name = 'activate'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]
