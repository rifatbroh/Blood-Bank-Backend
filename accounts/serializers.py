from accounts.models import DonorRegistrationModel,DonorProfile
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from events.models import DonationHistory


class DonorRegistrationSerializer(serializers.ModelSerializer):
    mobaile_no = serializers.CharField(max_length=12, required=True)
    age = serializers.IntegerField(required=True)
    address = serializers.CharField(required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email','mobaile_no','address','age', 'password', 'confirm_password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        age = self.validated_data['age']
        address = self.validated_data['address']
        mobaile_no = self.validated_data['mobaile_no']

        # Validate password confirmation
        if age<18:
            raise serializers.ValidationError("Age must be greater than 18 or equal.")
        
        if password != confirm_password:
            raise serializers.ValidationError({'error': "Passwords don't match"})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error': "Email already exists"})
        
        # Create the User object
        user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()
        DonorRegistrationModel.objects.create(
            user=user,
            age=age,
            mobaile_no=mobaile_no,
            address=address
        )
        # Create DonorProfile
        # Fetch the latest donation history for the user

        # Create the DonorProfile
        donor_profile = DonorProfile.objects.create(
            user=user,
            age=age,
            address=address,
            mobaile_no=mobaile_no,
        )
        donor_profile.save()
        
        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)





class DonorProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False, read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = DonorProfile
        fields = [
            'id', 'user', 'first_name', 'username', 'last_name', 'email',
            'age', 'mobaile_no', 'address', 'image', 'blood_group',
            'is_available', 'health_screening_passed'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'health_screening_passed': {'read_only': True},
            'is_available': {'read_only': True},
            'mobaile_no': {'read_only': False},
            'age': {'read_only': False},
            'blood_group': {'read_only': False},
            'username': {'read_only': True},
        }

    def update(self, instance, validated_data):
        # Nested user data update
        user_data = validated_data.pop('user', {})

        # Update user fields
        user = instance.user
        if user_data:  # Check if user_data is not empty
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.email = user_data.get('email', user.email)
            user.save()

        # Update DonorProfile fields
        instance.age = validated_data.get('age', instance.age)
        instance.mobaile_no = validated_data.get('mobaile_no', instance.mobaile_no)
        instance.address = validated_data.get('address', instance.address)
        instance.image = validated_data.get('image', instance.image)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.save()

        return instance