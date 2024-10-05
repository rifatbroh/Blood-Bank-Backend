from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import AboutUs, Contact, Feedback,DonorBlogPost,Subscription
from .serializers import AboutUsSerializer, ContactSerializer, FeedbackSerializer,BlogPostSerializer,SubscriptionSerializer
from events.models import DonationHistory,DonationEvent
from rest_framework.response import Response
from rest_framework import viewsets, status
from .constraints import OFFENSIVE_WORDS
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from events.views import  DonationEventPagination
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class AboutUsViewSet(viewsets.ModelViewSet):
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer

    def get_object(self):
        # Return the first About Us record
        return AboutUs.objects.first()


class ContactViewSet(viewsets.ModelViewSet):
    
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
   # Only allow POST requests




class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = DonorBlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = DonationEventPagination

    def perform_create(self, serializer):
        user = self.request.user
        title = serializer.validated_data.get('title')
        content = serializer.validated_data.get('content')

        # Check if title and content are empty
        if not title or not content:
            raise ValidationError(
                {"detail": "Title and content must be provided."}
            )

        # Check for offensive language
        if any(word in title.lower() for word in OFFENSIVE_WORDS) or any(word in content.lower() for word in OFFENSIVE_WORDS):
            raise ValidationError(
                {"detail": "Offensive language is not allowed."}
            )

        # Check if the user has valid donation history for the specified event
        has_valid_donation = DonationHistory.objects.filter(user=user).exists()

        if not has_valid_donation:
            raise ValidationError(
                {"detail": "You must have a valid donation history to create a blog post."}
            )

        # Save the blog post
        serializer.save(author=user)

        # Return a response with status 201
        return Response(
            {"detail": "Blog post created successfully!"},
            status=status.HTTP_201_CREATED
        )


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # Only return feedbacks for the logged-in user
        user = self.request.user
        if user.is_authenticated:
            return Feedback.objects.filter(donor=user)
        return Feedback.objects.none()  # Return empty queryset for unauthenticated users

    def perform_create(self, serializer):
        user = self.request.user
        print(user, "Logged in user")

        # Check if feedback already exists for this donor
        if Feedback.objects.filter(donor=user).exists():
            print("Feedback already exists for this donor")
            raise ValidationError("Your feedback already exists")

        # Check if the user has donation history before creating feedback
        if DonationHistory.objects.filter(user=user).exists():
            serializer.save(donor=user)
            return Response({"detail": "Thank you! Your feedback has been submitted successfully."}, status=status.HTTP_201_CREATED)
        else:
            raise ValidationError("We could not find your donation history. You must have a recorded donation in order to submit feedback.")



class All_Feddback(viewsets.ModelViewSet):
    queryset=Feedback.objects.all()
    serializer_class=FeedbackSerializer
    pagination_class=DonationEventPagination

    @action(detail=False,methods=['get'])
    def all_feedback(self,request):
        feedback=Feedback.objects.all()
        serializer=FeedbackSerializer(feedback,many=True)
        return Response({'all_feedback':serializer.data})



class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Create subscription for the logged-in user
        serializer.save(user=self.request.user)
