from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, UserSerializer, TwoFactorSetupSerializer,
    TwoFactorVerifySerializer, LoginSerializer, AdminUserSerializer
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

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Handles login - if 2FA is enabled, returns requires_2fa=True
    If not, returns tokens immediately
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    # Try to find user by email first (since that's our USERNAME_FIELD)
    user = None
    try:
        # First try to authenticate with the username as email
        user = authenticate(request, username=username, password=password)
        if not user:
            # If that fails, try to find user by username and authenticate with their email
            try:
                user_obj = User.objects.get(username=username)
                user = authenticate(request, username=user_obj.email, password=password)
            except User.DoesNotExist:
                # If that fails, try to find user by email directly
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.email, password=password)
                except User.DoesNotExist:
                    pass
    except Exception:
        pass

    if user is not None:
        if user.twofa:  # Using new field name
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

        # Authenticate using the login field (email or username)
        user = authenticate(username=login_field, password=password)
        if not user:
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
