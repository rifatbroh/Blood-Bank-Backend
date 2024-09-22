from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationEventViewSet, DonationHistoryViewSet,DonationEventFilter,DashboardViewSet,send_notification_to_active_users,NotificationViewSet





router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'donation-events', DonationEventViewSet, basename='donationevent')
router.register(r'donation-history', DonationHistoryViewSet, basename='donationhistory')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
urlpatterns = [
    path('', include(router.urls)),
    path('send-notification/all-active/<str:blood_group>/<str:location>/', send_notification_to_active_users, name='send_notification_all_active'),
    path('acceptdonation/<int:event_id>/', DonationEventViewSet.as_view({'post': 'accept'}), name='acceptdonation'),
    path('donation-event-filter/', DonationEventFilter.as_view(), name='donation-events-filter'),


]


# /api/blood-requests/?search=O+
# http://127.0.0.1:8000/events/donation-event-filter/?blood_group=A%2B
# http://127.0.0.1:8000/events/donation-event-filter/?blood_group=A-