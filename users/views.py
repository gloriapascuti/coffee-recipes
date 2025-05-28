from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import pyotp
import qrcode
from io import BytesIO
import base64
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, 
    LoginSerializer, 
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    TwoFactorDisableSerializer,
    AdminUserTableSerializer
)

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_2fa_enabled': user.is_2fa_enabled,
                    'is_special_admin': user.is_special_admin
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            # Get the login field (email or username) and password
            login_field = serializer.validated_data.get('login_field')
            password = serializer.validated_data['password']
            totp_code = serializer.validated_data.get('code')
            
            # Custom authentication using plain text password
            try:
                # Try to find user by email first, then by username
                user = None
                if '@' in login_field:
                    # It's an email
                    user = CustomUser.objects.get(email=login_field)
                else:
                    # It's a username
                    user = CustomUser.objects.get(username=login_field)
                
                if user.check_password(password):
                    # Check if 2FA is enabled
                    if user.is_2fa_enabled:
                        if not totp_code:
                            return Response({
                                'requires_2fa': True,
                                'message': 'Please provide the 6-digit code from your authenticator app'
                            }, status=status.HTTP_200_OK)
                        
                        # Verify TOTP code
                        if user.totp_secret:
                            totp = pyotp.TOTP(user.totp_secret)
                            if not totp.verify(totp_code, valid_window=1):
                                return Response({
                                    'error': 'Invalid authentication code'
                                }, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({
                                'error': '2FA is enabled but not properly configured'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'first_name': user.first_name,
                            'last_name': user.last_name,
                            'is_2fa_enabled': user.is_2fa_enabled,
                            'is_special_admin': user.is_special_admin
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Invalid credentials'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TwoFactorSetupView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFactorSetupSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Verify the email matches the authenticated user
            if request.user.email != email:
                return Response({
                    'error': 'Email does not match authenticated user'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate TOTP secret
            secret = pyotp.random_base32()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate QR code
            provisioning_uri = totp.provisioning_uri(
                name=email,
                issuer_name="Coffee Website"
            )
            
            # Create QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            # Store the secret temporarily (will be saved when verified)
            request.user.totp_secret = secret
            request.user.save()
            
            return Response({
                'qr_code': f'data:image/png;base64,{img_str}',
                'secret': secret,
                'message': 'Scan the QR code with your authenticator app and enter the 6-digit code to verify'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TwoFactorVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        if serializer.is_valid():
            totp_code = serializer.validated_data['totp_code']
            
            if not request.user.totp_secret:
                return Response({
                    'error': 'No TOTP secret found. Please setup 2FA first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify the TOTP code
            totp = pyotp.TOTP(request.user.totp_secret)
            if totp.verify(totp_code, valid_window=1):
                # Enable 2FA for the user
                request.user.is_2fa_enabled = True
                request.user.save()
                
                return Response({
                    'message': '2FA has been successfully enabled for your account'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid authentication code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TwoFactorDisableView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = TwoFactorDisableSerializer(data=request.data)
        if serializer.is_valid():
            totp_code = serializer.validated_data['totp_code']
            
            if not request.user.is_2fa_enabled:
                return Response({
                    'error': '2FA is not enabled for your account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not request.user.totp_secret:
                return Response({
                    'error': 'No TOTP secret found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify the TOTP code
            totp = pyotp.TOTP(request.user.totp_secret)
            if totp.verify(totp_code, valid_window=1):
                # Disable 2FA for the user
                request.user.is_2fa_enabled = False
                request.user.totp_secret = None
                request.user.save()
                
                return Response({
                    'message': '2FA has been successfully disabled for your account'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid authentication code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'address': user.address,
            'is_2fa_enabled': user.is_2fa_enabled,
            'is_special_admin': user.is_special_admin
        })

class AdminUserTableView(generics.ListAPIView):
    """
    View for special admin to see all users in a table format.
    Only accessible by users with is_special_admin=True
    """
    serializer_class = AdminUserTableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow special admin to access this view
        if not self.request.user.is_special_admin:
            raise PermissionDenied("Access denied. Special admin privileges required.")
        
        return CustomUser.objects.all().order_by('-date_joined')
    
    def list(self, request, *args, **kwargs):
        # Double check permission
        if not request.user.is_special_admin:
            return Response(
                {"error": "Access denied. Special admin privileges required."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().list(request, *args, **kwargs) 