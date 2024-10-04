from django.shortcuts import render, redirect
from .serializers import DonorRegistrationSerializer, UserLoginSerializer,DonorProfileSerializer
from .models import DonorRegistrationModel,DonorProfile
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from django.urls import path, include

class UserRegistrationView(APIView):
    serializer_class = DonorRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # DonorProfile.objects.create(user=user)

            token = default_token_generator.make_token(user)
            print("token", token)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            print('Uid', uid)
            confirm_link = f"http://127.0.0.1:8000/accounts/active/{uid}/{token}/"
            email_subject = "Confirm Your Email"
            email_body = render_to_string("confirm_email.html", {"confirm_link": confirm_link})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, 'text/html')
            email.send()
            return Response("Form submission done. Check your email.", status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def activate(request, uid, token):
    try:
        uid = urlsafe_base64_decode(uid).decode()
        print(uid)
        user = User._default_manager.get(pk=uid)
        print(user)
    except User.DoesNotExist:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("http://127.0.0.1:5500/login.html")
    else:
        return Response({'error':"activation_failed"})  # Add a template or view to handle activation failure




class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                print(token,_)
                return Response({'token': token.key,'user_id': user.id}, status=status.HTTP_200_OK)
                # return redirect("http://127.0.0.1:5500/login.html")
            else:
                return Response({'error': "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserLogoutView(APIView):
    def post(self, request):
        try:
            user = request.user
            print(user)
            token = Token.objects.get(user=user)
            print(token)
            token.delete()
            logout(request)
            return Response({"ok": True})
            # return redirect('login')
        except Token.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)



# class DonorProfileView(viewsets.ModelViewSet):
#     serializer_class = DonorProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return DonorProfile.objects.filter(user=self.request.user)
    

class DonorProfileView(viewsets.ModelViewSet):
    serializer_class = DonorProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return DonorProfile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)  # Allow partial updates
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
