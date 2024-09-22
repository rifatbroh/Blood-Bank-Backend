from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AboutUs, BlogPost, Contact, Feedback
from .serializers import AboutUsSerializer, BlogPostSerializer, ContactSerializer, FeedbackSerializer
from events.models import DonationHistory
from rest_framework.response import Response
from rest_framework import viewsets, status
from .constraints import OFFENSIVE_WORDS



from datetime import timedelta
from django.utils import timezone

class AboutUsViewSet(viewsets.ModelViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        # Return the first About Us record
        return AboutUs.objects.first()


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    http_method_names = ['post']  # Only allow POST requests




class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content')

        # Check if title and content are empty
        if not title or not content:
            return Response(
                {"detail": "Title and content must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )



        # Check for offensive language
        if any(word in title.lower() for word in OFFENSIVE_WORDS) or any(word in content.lower() for word in OFFENSIVE_WORDS):
            return Response(
                {"detail": "Offensive language is not allowed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the event ID from the request data
        event_id = self.request.data.get('event_id')

        # Check if the event ID is provided
        if not event_id:
            return Response(
                {"detail": "Event ID must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has valid donation history for the specified event
        has_valid_donation = DonationHistory.objects.filter(
            user=user,
            event__id=event_id,
            is_canceled=False
        ).exists()

        if not has_valid_donation:
            return Response(
                {"detail": "You must have a valid donation history for the specified event to create a blog post."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Save the blog post
        serializer.save(author=user)
        return Response(
            {"detail": "Blog post created successfully!"},
            status=status.HTTP_201_CREATED
        )



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        event_id = self.request.data.get('event_id')

        # 1. Check if the user has donation history for the event (অনুমোদিত ইভেন্টের জন্য)
        donation = DonationHistory.objects.filter(user=user, event_id=event_id).first()
        if not donation:
            return Response(
                {"detail": "You can only submit feedback for events where you have donated."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Check if feedback is being submitted within 7 days of donation (ফিডব্যাক টাইম ফ্রেম)
        time_since_donation = timezone.now() - donation.accepted_on
        if time_since_donation > timedelta(days=7):
            return Response(
                {"detail": "You can only submit feedback within 7 days of donation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Check if the user has already submitted feedback for this event (ফিডব্যাক লিমিটেশন)
        if Feedback.objects.filter(donor=user, event_id=event_id).exists():
            return Response(
                {"detail": "You have already submitted feedback for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the feedback
        serializer.save(donor=user)

        # Success message after successful feedback submission
        return Response(
            {"Your feedback has been successfully submitted!"},
            status=status.HTTP_201_CREATED
        )
