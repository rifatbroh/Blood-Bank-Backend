from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationEventViewSet, DonationHistoryViewSet,DonationEventFilter,DashboardViewSet,NotificationViewSet





router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'donation-events', DonationEventViewSet, basename='donationevent')
router.register(r'donation-history', DonationHistoryViewSet, basename='donationhistory')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
urlpatterns = [
    path('', include(router.urls)),
    path('acceptdonation/<int:event_id>/', DonationEventViewSet.as_view({'post': 'accept'}), name='acceptdonation'),
    path('donation-event-filter/', DonationEventFilter.as_view(), name='donation-events-filter'),


]


# /api/blood-requests/?search=O+
# http://127.0.0.1:8000/events/donation-event-filter/?blood_group=A%2B
# http://127.0.0.1:8000/events/donation-event-filter/?blood_group=A-