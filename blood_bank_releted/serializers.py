from rest_framework import serializers
from .models import AboutUs

from rest_framework import serializers
from .models import Contact
# from .models import BlogPost
from .models import Feedback,DonorBlogPost,Subscription








class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['id', 'title', 'description', 'mission', 'vision', 'created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message', 'created_at']


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.get_full_name', read_only=True)  # Corrected spelling to 'donor'

    class Meta:
        model = DonorBlogPost
        fields = ['id', 'title','image', 'content', 'author', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    donor = serializers.CharField(source='donor.get_full_name', read_only=True)  # Corrected spelling to 'donor'

    class Meta:
        model = Feedback
        fields = ['id', 'donor', 'feedback', 'rating', 'created_at']  # Use 'donor' in fields as well

from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'created_at']
        read_only_fields = ['created_at']  # created_at should be read-only
