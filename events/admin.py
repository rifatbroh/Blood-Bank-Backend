from django.contrib import admin
from .models import DonationEvent, DonationHistory,Notification

@admin.register(DonationEvent)
class DonationEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'recipient', 'blood_group','date', 'is_active', 'created_by', 'status')

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'accepted_on', 'is_canceled', 'blood_donation_count')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display=('sender','recipient','location','blood_group','message','is_read')