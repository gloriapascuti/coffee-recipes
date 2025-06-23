from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, UserSerializer, TwoFactorSetupSerializer,
    TwoFactorVerifySerializer, LoginSerializer, AdminUserSerializer, ProfileSerializer
)
import pyotp
import qrcode
import base64
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.utils import timezone

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'twofa': user.twofa
        }, status=status.HTTP_201_CREATED)

class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login with email/username and password, with optional 2FA
    """
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')

    # Use email if provided, otherwise use username
    login_field = email if email else username

    if not login_field or not password:
        return Response({'error': 'Email/username and password are required'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    # Authenticate user
    user = authenticate(username=login_field, password=password)
    if user:
        if user.twofa and user.totp_secret:  # Using new field name
            # If 2FA is enabled, return a flag indicating this and don't issue tokens yet
            return Response({'requires_2fa': True, 'email': user.email})
        else:
            # If 2FA is not enabled, proceed with login and issue tokens
            # Update last_login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'twofa': user.twofa,  # Using new field name
                'is_special_admin': user.is_special_admin
            })
    else:
        # Check if it's a banned user trying to login
        try:
            potential_user = User.objects.get(username=login_field)
            if potential_user.check_password(password) and potential_user.is_banned:
                return Response({
                    'error': 'Your account has been banned due to suspicious activity. Please re-register with the same credentials if you wish to continue.'
                }, status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            pass
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa_login(request):
    """
    Verifies the 2FA code during login and issues tokens if successful
    """
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.twofa or not user.totp_secret:
        return Response({'error': '2FA not enabled for this user'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(code):
        # Update last_login on successful 2FA verification
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Issue tokens after successful 2FA verification
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'username': user.username,
            'twofa': user.twofa,
            'is_special_admin': user.is_special_admin
        })
    else:
        return Response({'error': 'Invalid 2FA code'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """
    Sets up 2FA with email and generates QR code
    """
    user = request.user
    email = request.data.get('email')
    
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate a new secret
    secret = pyotp.random_base32()
    user.totp_secret = secret
    user.twofa_email = email
    user.save()

    totp = pyotp.TOTP(secret)
    qr_code_url = totp.provisioning_uri(email, issuer_name='Coffee Website')
    
    # Generate QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code = base64.b64encode(buffered.getvalue()).decode()

    return Response({
        'qr_code': qr_code,
        'secret': secret
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_2fa_setup(request):
    """
    Verifies the 2FA setup code and enables 2FA
    """
    user = request.user
    code = request.data.get('code')
    
    if not code:
        return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.totp_secret:
        return Response({'error': '2FA setup not initiated'}, status=status.HTTP_400_BAD_REQUEST)

    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(code):
        user.twofa = True  # Using new field name
        user.save()
        return Response({'message': '2FA enabled successfully'})
    else:
        return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Simply disables 2FA - no code required as per user requirements
    """
    user = request.user
    user.twofa = False  # Using new field name
    user.totp_secret = None
    user.twofa_email = None
    user.save()
    return Response({'message': '2FA disabled successfully'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_2fa_status(request):
    """
    Returns the current 2FA status for the user
    """
    user = request.user
    return Response({
        'twofa': user.twofa,
        'email': user.twofa_email
    })

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        login_field = serializer.validated_data['login_field']
        password = serializer.validated_data['password']
        code = serializer.validated_data.get('code')

        # Try to authenticate using the login field (email or username)
        user = authenticate(username=login_field, password=password)
        
        # If authentication fails, check if it's because the user is banned
        if not user:
            try:
                # Try to find the user manually to check if they're banned
                potential_user = User.objects.get(username=login_field)
                if potential_user.check_password(password) and potential_user.is_banned:
                    return Response(
                        {'error': 'Your account has been banned due to suspicious activity. Please re-register with the same credentials if you wish to continue.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except User.DoesNotExist:
                pass
            
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user.twofa:  # Using new field name
            if not code:
                return Response(
                    {'require_2fa': True},
                    status=status.HTTP_200_OK
                )

            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(code):
                return Response(
                    {'error': 'Invalid 2FA code'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_users_list(request):
    """
    List all users - only accessible by special admin
    """
    if not request.user.is_special_admin:
        return Response({'error': 'Permission denied. Special admin access required.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_user_activity(request, user_id):
    """
    Admin can verify a user's suspicious activity and mark it as not suspicious
    The count increases by 1 and the user is not red anymore
    """
    if not request.user.is_special_admin:
        return Response({'error': 'Permission denied. Special admin access required.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Increment the suspicious activity count by 1 and mark user as not suspicious anymore
    user.suspicious_activity_count += 1
    user.is_currently_suspicious = False
    user.last_suspicious_check_date = timezone.now()
    user.save(update_fields=['suspicious_activity_count', 'is_currently_suspicious', 'last_suspicious_check_date'])
    
    return Response({'message': 'User activity verified successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ban_user(request, user_id):
    """
    Admin can ban a user after 3 suspicious activity incidents
    """
    if not request.user.is_special_admin:
        return Response({'error': 'Permission denied. Special admin access required.'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user has 3 or more suspicious activity counts
    if user.suspicious_activity_count < 3:
        return Response({'error': 'User must have 3 or more suspicious activity incidents to be banned'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Ban the user
    user.is_banned = True
    user.is_active = False  # Deactivate account
    user.is_currently_suspicious = False  # Remove suspicious flag since they're banned
    user.last_suspicious_check_date = timezone.now()
    user.save(update_fields=['is_banned', 'is_active', 'is_currently_suspicious', 'last_suspicious_check_date'])
    
    return Response({'message': 'User has been banned successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_notification_status(request):
    """
    Get the current user's notification status (if they're under investigation)
    """
    user = request.user
    
    if user.is_banned:
        return Response({
            'status': 'banned',
            'message': 'Your account has been banned due to suspicious activity. Please re-register.'
        })
    elif user.suspicious_activity_count >= 3:
        return Response({
            'status': 'high_risk',
            'message': 'You where under investigation too many times and can be banned any time, if you are banned you will be able to log in again, but all your account will be reset'
        })
    elif user.is_currently_suspicious:
        return Response({
            'status': 'under_investigation',
            'message': 'Under investigation - noticed suspicious activity'
        })
    else:
        return Response({
            'status': 'normal',
            'message': 'Account status is normal'
        })
