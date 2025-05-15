from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import CustomUser, EmailVerification
from .email_utils import generate_verification_code, send_verification_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'is_email_verified')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password')
        
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # User will be inactive until email is verified
        )
        
        # Generate verification code
        verification_code = generate_verification_code()
        
        # Create verification record
        EmailVerification.objects.create(
            user=user,
            code=verification_code,
            expires_at=timezone.now() + timezone.timedelta(minutes=30)
        )
        
        # Send verification email
        send_verification_email(user.email, verification_code)
        
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        
        if not user:
            raise serializers.ValidationError("Invalid credentials. Please try again.")
        
        if not user.is_active:
            raise serializers.ValidationError("Account is not active. Please verify your email.")
            
        if not user.is_email_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email.")
        
        return {
            'user': user,
            'email': user.email
        }


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(min_length=6, max_length=6)
    
    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        try:
            verification = EmailVerification.objects.filter(
                user=user,
                code=data['verification_code']
            ).latest('created_at')
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code.")
            
        if not verification.is_valid():
            raise serializers.ValidationError("Verification code has expired. Please request a new one.")
            
        return {
            'user': user,
            'verification': verification
        }


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'])
            return {'user': user}
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.") 