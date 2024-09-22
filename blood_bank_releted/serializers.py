from rest_framework import serializers
from .models import AboutUs

from rest_framework import serializers
from .models import Contact
from .models import BlogPost
from .models import Feedback








class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = ['id', 'title', 'description', 'mission', 'vision', 'created_at', 'updated_at']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message', 'created_at']


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'donor', 'feedback', 'response', 'created_at']
