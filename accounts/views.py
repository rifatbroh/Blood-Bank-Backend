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
import requests


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


# IMAGEBB_API_URL = 'https://api.imgbb.com/1/upload'  # ImageBB API URL
# IMAGEBB_API_KEY = 'ca0a7f8e97446e4139d17010b039c2da'
   
class DonorProfileView(viewsets.ModelViewSet):
    queryset=DonorProfile
    serializer_class = DonorProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return DonorProfile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow partial updates
        instance = self.get_object()
        
        # Remove image upload logic
        # Handle image upload (removed)

        # Proceed with the regular update process
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


    # def upload_image_to_imgbb(self, image):
    #     try:
    #         # Read the image file as binary
    #         image_data = image.read()  # Read the image directly from the uploaded file
            
    #         # Prepare the payload
    #         payload = {
    #             'key': IMAGEBB_API_KEY,
    #             'image': image_data,  # Use the binary data of the image
    #         }
    #         print("Uploading image to ImageBB...")
    #         print(f"API Key: {IMAGEBB_API_KEY}")  # এই লাইনে API কীটি প্রকাশ করবেন না।
    #         # print(f"Payload: {payload}")  # Payload লগ করুন
    #         # Send the request to ImageBB
    #         response = requests.post(IMAGEBB_API_URL, files=payload, timeout=30)  # Use 'files' instead of 'data'
    #         response_data = response.json()
    #         # print(response_data)

    #         # Check for success in the response
    #         if response.status_code == 200:
                
    #             image_url = response.json()['data']['url']  # Return the uploaded image URL
    #             print("Image uploaded successfully:", image_url)
    #         else:
    #             print("Image upload failed:", response.json())  # Log the error response
    #             return None  # Handle the error as needed
    #     except requests.exceptions.Timeout:
    #         print("Image upload timed out.")
    #         return None  # Or raise an exception/message
    #     except Exception as e:
    #         print("An error occurred:", str(e))
    #         return None  # Or raise an exception/message

    # def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Allow partial updates
        instance = self.get_object()
        image = request.FILES.get('image')
        print(image,"image")
        # Handle image upload
        if image:
            image_url = self.upload_image_to_imgbb(image)
            print(image_url,"image_url")
            if image_url:
                request.data['image'] = image_url  # Use the URL returned by ImageBB
                print(request.data['image'])
            else:
                return Response({"error": "Image upload failed."}, status=400)  # Return error response

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)