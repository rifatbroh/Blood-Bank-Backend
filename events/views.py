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
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
import pytz
from rest_framework.permissions import IsAuthenticatedOrReadOnly





class DonationEventPagination(PageNumberPagination):
    page_size =5  # প্রতি পৃষ্ঠায় ১০টি ইভেন্ট দেখাবে
    page_size_query_param = 'page_size'
    max_page_size = 100



class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class=DonationEventPagination
    

    def perform_create(self, serializer, sender, recipient):
        # এখানে নোটিফিকেশন তৈরি করুন
        serializer.save(sender=sender, recipient=recipient)

    def get_queryset(self):
        # শুধুমাত্র লগ-ইন ইউজারের নোটিফিকেশন দেখানো হবে
        return Notification.objects.all().order_by('-created_at')
        # return Notification.objects.all().order_by('-created_at')

    def create(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in to create a notification.'}, status=status.HTTP_401_UNAUTHORIZED)

        # নতুন নোটিফিকেশন ডেটা
        sender=request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blood_group = serializer.validated_data['blood_group']
        location = serializer.validated_data['location']# Convert location to lowercase
        message = serializer.validated_data['message']
        
        print(blood_group, location, message)

        # সক্রিয় ব্যবহারকারীদের তালিকা
        active_users = User.objects.filter(is_active=True)

        for user in active_users:
            # চেক করুন যে একই user এবং blood group এর জন্য নোটিফিকেশন বিদ্যমান কিনা
            existing_notification = Notification.objects.filter(
                
                sender=sender,
                blood_group=blood_group,
                location=location
            ).exists()

        if  existing_notification:
            return Response({'error': f'A notification for user {user.username} , blood group {blood_group} and location {location}  already exists.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # নতুন নোটিফিকেশন তৈরি করুন
        Notification.objects.create(
            sender=request.user,
            recipient=user,  # প্রত্যেক সক্রিয় ইউজারের জন্য রিসিপিয়েন্ট সেট করুন
            blood_group=blood_group,
            location=location,  # Save the lowercase location
            message=message
        )

        return Response({'Notifications sent successfully to all active users.'}, status=status.HTTP_201_CREATED)



class DonationEventViewSet(viewsets.ModelViewSet):
    queryset = DonationEvent.objects.filter(is_active=True)
    serializer_class = DonationEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    # pagination_class = DonationEventPagination

    def perform_create(self, serializer):
       
        event_name=serializer.validated_data['event_name']
        blood_group=serializer.validated_data['blood_group']
        date_str = serializer.validated_data.get('date')
        print(date_str)
        
        notification=Notification.objects.filter(blood_group=blood_group,location=event_name).exists()
        if not notification:
            raise serializers.ValidationError({
                'error': f'Currently, there are no available events for "{event_name}" with blood group "{blood_group}" if we need blood we will notification send you.'
            })
        print(event_name,blood_group)
        user = self.request.user
        event=DonationEvent.objects.filter(created_by=user,event_name=event_name,blood_group=blood_group).exists()
        print(event)
        if  event:
            raise serializers.ValidationError({'error': f'A Event for user {user} event name {event_name} and blood group {blood_group} already exists.'})

        donation_event = serializer.save(created_by=self.request.user)
        print(f"Saved Event ID: {donation_event.id}, Created By: {donation_event.created_by}")


    def get_queryset(self):
        print(f"Current User: {self.request.user}")  # ইউজার প্রদর্শন করুন
        event = DonationEvent.objects.filter(created_by=self.request.user)
        print(event)  
        return event

    @action(detail=False, methods=['post'], url_path=r'acceptdonation/(?P<event_id>\d+)')
    def accept(self, request, event_id):
        print(event_id)
        try:
            # Check if the event exists
            event = DonationEvent.objects.get(id=event_id)

            # Check if the user has a notification for this event
            notification = Notification.objects.filter(
                recipient=request.user,
                blood_group=event.blood_group,
                location=event.event_name
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

            # # Check the donation interval
            # min_donation_interval = timedelta(days=56)
            # if donation_history.accepted_on:
            #     accepted_date = donation_history.accepted_on.date()  # Convert datetime to date
            #     current_date = timezone.now().date()

            #     if current_date < accepted_date + min_donation_interval:
            #         return Response({"error": "You must wait at least 56 days between donations."}, status=status.HTTP_400_BAD_REQUEST)

            # # Update DonorProfile
            # donor_profile.blood_donation_count += 1
            donor_profile.health_screening_passed = True
            donor_profile.is_available=False
            donor_profile.save()

            event.status="completed"
            event.save()

            donation_history.blood_donation_count+=1
            donation_history.save()


            # Delete the notification
            if notification:
                notification.delete()

            return Response({"message": "Donation accepted successfully!"}, status=status.HTTP_201_CREATED)
        except DonationEvent.DoesNotExist:
            return Response({"error": "Event not found!"}, status=status.HTTP_400_BAD_REQUEST)



# Viewset for DonationHistory
class DonationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DonationHistorySerializer
    permission_classes=[IsAuthenticated]

    
    def get_queryset(self):
        # Only show the current user's donation history
        return DonationHistory.objects.filter(user=self.request.user)




class DonationEventFilter(generics.ListAPIView):
    serializer_class = DonationEventSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['blood_group']
    pagination_class = DonationEventPagination  # Pagination class যুক্ত করা হলো

    ordering = ['-id']  # Id অনুযায়ী ডিফল্ট অর্ডারিং

    def get_queryset(self):
        queryset = DonationEvent.objects.filter(is_active=True)
        
        # Query parameters নেয়া
        blood_group = self.request.query_params.get('blood_group')
        event_name = self.request.query_params.get('event_name')
        print(blood_group,event_name)
        # যদি শুধু blood group দেওয়া থাকে
        if blood_group and not event_name:
            # decoded_blood_group = unquote_plus(blood_group)
            queryset = queryset.filter(blood_group=blood_group)
            print(queryset)
        
        # যদি শুধু event name দেওয়া থাকে
        elif event_name and not blood_group:
            # decoded_event_name = unquote_plus(event_name)
            queryset = queryset.filter(event_name__icontains=event_name)
            print(queryset)
        return queryset




class DashboardViewSet(viewsets.ModelViewSet):
    queryset = DonationEvent.objects.all()  # Default queryset
    serializer_class = DonationEventSerializer
    pagination_class=DonationEventPagination
    # permission_classes=[IsAuthenticatedOrReadOnly]



    # Custom action for recipient requests
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def recipient_requests(self, request):
        if request.user.is_authenticated:
         # যদি ইউজার অথেনটিকেটেড থাকে, তখন exclude(created_by=request.user) ফিল্টার প্রয়োগ করবে
            recipient_requests = DonationEvent.objects.filter(is_active=True).exclude(created_by=request.user)
        else:
            # যদি ইউজার অ্যানোনিমাস হয়, exclude প্রয়োগ না করে শুধু is_active=True ফিল্টার করবে
            recipient_requests = DonationEvent.objects.filter(is_active=True)

        # রেসপন্সে ইভেন্টগুলো পাঠানোর জন্য সিরিয়ালাইজার ব্যবহার করুন
        serializer = DonationEventSerializer(recipient_requests, many=True)
        return Response({'recipient_requests': serializer.data})

    # Custom action for donation history
    @action(detail=False, methods=['get'])
    def donation_history(self, request):
        donation_history = DonationHistory.objects.all()
        serializer = DonationHistorySerializer(donation_history, many=True)
        return Response({'donation_history': serializer.data})
    


# class All_Feddback(viewsets.ModelViewSet):
#     serializer_class=
