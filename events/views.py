from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from .models import DonationEvent, DonationHistory
from .serializers import DonationEventSerializer, DonationHistorySerializer
from accounts.models import DonorProfile
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters
from urllib.parse import unquote_plus
from .models import Notification
from django.contrib.auth.models import User
from .serializers import NotificationSerializer
from django.http import HttpResponse





def send_notification_to_active_users(request, blood_group, location):
    # শুধুমাত্র active ইউজারদের ফিল্টার করা হবে
    active_users = User.objects.filter(is_active=True)
    
    message = f"Blood needed for {blood_group} at {location}. Please donate if available."

    for user in active_users:
        # চেক করুন যে, ওই ইউজারকে একই ব্লাড গ্রুপের জন্য নোটিফিকেশন পাঠানো হয়েছে কিনা
        if not Notification.objects.filter(
                    recipient=user,
                    blood_group=blood_group,
                    location=location
                ).exists():
            Notification.objects.create(
                sender=request.user,
                recipient=user,
                blood_group=blood_group,
                location=location,
                message=message
            )
        else:
            return HttpResponse({"Notification for blood group type alredy exists"},status=status.HTTP_400_BAD_REQUEST)
    
    return HttpResponse ({"Notifications sent to active users."})



class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # শুধুমাত্র লগ-ইন ইউজারের নোটিফিকেশন দেখানো হবে
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


class DonationEventViewSet(viewsets.ModelViewSet):
    queryset = DonationEvent.objects.filter(is_active=True)
    serializer_class = DonationEventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return DonationEvent.objects.filter(is_active=True).exclude(created_by=self.request.user)

    @action(detail=False, methods=['post'], url_path=r'acceptdonation/(?P<event_id>\d+)')
    def accept(self, request, event_id):
        try:
            # Check if the event exists
            event = DonationEvent.objects.get(id=event_id)

            # Check if the user has a notification for this event
            notification = Notification.objects.filter(
                recipient=request.user,
                blood_group=event.blood_group,
            ).first()

            if not notification:
                return Response({"error": "You do not have a notification for this donation event!"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the user has already accepted this event
            if DonationHistory.objects.filter(user=request.user, event=event).exists():
                return Response({"error": "You have already accepted this donation event!"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the DonorProfile for the current user
            donor_profile = get_object_or_404(DonorProfile, user=request.user)

            # Create a donation history record
            donation_history = DonationHistory.objects.create(user=request.user, event=event)

            # Check the donation interval
            min_donation_interval = timedelta(days=56)
            if donation_history.accepted_on:
                accepted_date = donation_history.accepted_on.date()  # Convert datetime to date
                current_date = timezone.now().date()

                if current_date < accepted_date + min_donation_interval:
                    return Response({"error": "You must wait at least 56 days between donations."}, status=status.HTTP_400_BAD_REQUEST)

            # Update DonorProfile
            donor_profile.blood_donation_count += 1
            donor_profile.health_screening_passed = True
            donor_profile.save()

            # Delete the notification
            if notification:
                notification.delete()

            return Response({"message": "Donation accepted successfully!"}, status=status.HTTP_201_CREATED)
        except DonationEvent.DoesNotExist:
            return Response({"error": "Event not found!"}, status=status.HTTP_400_BAD_REQUEST)



# Viewset for DonationHistory
class DonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only show the current user's donation history
        return DonationHistory.objects.filter(user=self.request.user)





class DonationEventFilter(generics.ListAPIView):
    serializer_class = DonationEventSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['blood_group']
    ordering = ['-id']

    def get_queryset(self):
        queryset = DonationEvent.objects.filter(is_active=True)
        blood_group = self.request.query_params.get('blood_group')
        if blood_group:
            decoded_blood_group = unquote_plus(blood_group)  # Decode the URL using unquote_plus
            queryset = queryset.filter(blood_group=decoded_blood_group)
        return queryset





class DashboardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DonationEvent.objects.all()  # Default queryset
    serializer_class = DonationEventSerializer

    # Custom action for recipient requests
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recipient_requests(self, request):
        recipient_requests = DonationEvent.objects.filter(is_active=True).exclude(created_by=request.user)
        print(recipient_requests)
        serializer = DonationEventSerializer(recipient_requests, many=True)
        return Response({'recipient_requests': serializer.data})

    # Custom action for donation history
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def donation_history(self, request):
        donation_history = DonationHistory.objects.filter(user=request.user)
        serializer = DonationHistorySerializer(donation_history, many=True)
        return Response({'donation_history': serializer.data})
    



