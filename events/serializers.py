from rest_framework import serializers
from .models import DonationEvent, DonationHistory
from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models import DonorProfile
from .models import Notification
from rest_framework.response import Response
from rest_framework import status


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'recipient', 'blood_group', 'location', 'message', 'created_at', 'is_read']



# Donation Event Serializer
class DonationEventSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = DonationEvent
        fields = ['id', 'event_name', 'recipient', 'blood_group', 'is_active', 'created_by', 'status']

    def validate(self, data):
        request = self.context['request']
        
        # Check if the user has donation history
        donation_history = DonationHistory.objects.filter(user=request.user).first()
        if not donation_history:
            raise ValidationError("Donor History not found.")

        # Check the donation interval
        min_donation_interval = timedelta(days=56)
        if donation_history.accepted_on:
            accepted_date = donation_history.accepted_on.date()  # Convert datetime to date
            current_date = timezone.now().date()

            if current_date < accepted_date + min_donation_interval:
                raise ValidationError("You must wait at least 56 days between donations.")

        return data
# Donation History Serializer
class DonationHistorySerializer(serializers.ModelSerializer):
    event = DonationEventSerializer(read_only=True)
    # user = serializers.CharField(source='user.get_full_name', read_only=True)


    class Meta:
        model = DonationHistory
        fields = ['id', 'user', 'event', 'accepted_on', 'is_canceled']


