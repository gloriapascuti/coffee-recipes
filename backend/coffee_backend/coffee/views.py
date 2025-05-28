# import os
# from django.conf import settings
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
#
# from rest_framework import status
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
# from rest_framework.authtoken.models import Token
# from rest_framework.authtoken.views import ObtainAuthToken
#
# from .models.coffee import Coffee, Origin
# from .models.uploads import UploadedFile
# from .serializers import (
#     CoffeeSerializer,
#     OriginSerializer,
#     UploadedFileSerializer,
#     RegisterSerializer,
#     LoginSerializer,
#     UserSerializer,
# )
# from .models import UserProfile
#
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def healthcheck(request):
#     return Response({"status": "ok"})
#
#
# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response(
#             {"token": token.key, "user_id": user.id, "username": user.username},
#             status=status.HTTP_201_CREATED
#         )
#
#
# class LoginView(ObtainAuthToken):
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         serializer = LoginSerializer(data=request.data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, _ = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.id,
#             'username': user.username
#         })
#
#
# def log_user_operation(user, operation):
#     try:
#         profile = user.userprofile
#         if profile.users_operations:
#             profile.users_operations += f",{operation}"
#         else:
#             profile.users_operations = operation
#         profile.save()
#     except Exception as e:
#         print("Failed to log user operation:", e)
#
#
# class CoffeeViewSets(APIView):
#     """
#     GET    /api/coffee/         → admin sees all; others only their own
#     POST   /api/coffee/         → authenticated only
#     PUT    /api/coffee/<pk>/    → authenticated only
#     DELETE /api/coffee/<pk>/    → authenticated only
#     """
#     permission_classes = [IsAuthenticatedOrReadOnly]
#
#     def get(self, request):
#         qs = Coffee.objects.select_related('origin', 'user')
#         # Show all coffees to all users
#         data = CoffeeSerializer(qs, many=True, context={'request': request}).data
#         return Response(data)
#
#     def post(self, request):
#         if not request.user or not request.user.is_authenticated:
#             return Response(
#                 {"detail": "Authentication credentials were not provided."},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#         # Defensive: check user exists in DB
#         try:
#             user = User.objects.get(pk=request.user.id)
#         except User.DoesNotExist:
#             return Response(
#                 {"detail": "User does not exist."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         data = request.data.copy()
#         # Do not set 'user' in data, serializer will use request.user
#         serializer = CoffeeSerializer(data=data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         coffee = serializer.save()
#         log_user_operation(request.user, "add")
#         return Response(
#             CoffeeSerializer(coffee, context={'request': request}).data,
#             status=status.HTTP_201_CREATED
#         )
#
#     def put(self, request, pk):
#         coffee = get_object_or_404(Coffee, pk=pk)
#         data = request.data.copy()
#         data['user'] = coffee.user.id
#         serializer = CoffeeSerializer(coffee, data=data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         coffee = serializer.save()
#         log_user_operation(request.user, "edit")
#         return Response(CoffeeSerializer(coffee, context={'request': request}).data)
#
#     def delete(self, request, pk):
#         coffee = get_object_or_404(Coffee, pk=pk)
#         coffee.delete()
#         log_user_operation(request.user, "delete")
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#
# class OriginViewSet(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request):
#         origins = Origin.objects.all()
#         return Response(OriginSerializer(origins, many=True).data)
#
#
# class FileUploadView(APIView):
#     permission_classes = [AllowAny]
#     parser_classes = (MultiPartParser, FormParser)
#
#     def post(self, request, format=None):
#         serializer = UploadedFileSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def get(self, request):
#         folder = os.path.join(settings.MEDIA_ROOT, 'uploads')
#         files = os.listdir(folder)
#         return Response({"files": files})
#
#
# class UserList(APIView):
#     """
#     GET /api/users/ → admin only
#     """
#     permission_classes = [IsAdminUser]
#
#     def get(self, request):
#         qs = User.objects.all()
#         return Response(UserSerializer(qs, many=True).data)


# coffee/views.py

import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models.coffee import Coffee, Origin
from .models.uploads import UploadedFile
from .serializers import (
    CoffeeSerializer,
    OriginSerializer,
    UploadedFileSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthUserSerializer,
    OperationSerializer,
)
from .models.operations import Operation
from .models.user import User
from django.contrib.auth.models import User as AuthUser
from .models.user_profile import UserProfile

@api_view(['GET'])
@permission_classes([AllowAny])
def healthcheck(request):
    return Response({"status": "ok"})


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'username': user.username
        })


def log_user_operation(user, operation):
    try:
        Operation.objects.create(user=user, operation=operation)
        # Update users_operations in UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        before = profile.users_operations
        after = f"{before},{operation}" if before else operation
        profile.users_operations = after
        profile.save(update_fields=['users_operations'])
    except Exception as e:
        print("Failed to log user operation:", e)


class CoffeeViewSet(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Coffee.objects.select_related('origin', 'user')
        serializer = CoffeeSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = CoffeeSerializer(data=request.data.copy(), context={'request': request})
        serializer.is_valid(raise_exception=True)
        coffee = serializer.save()
        return Response(
            CoffeeSerializer(coffee, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def put(self, request, pk):
        coffee = get_object_or_404(Coffee, pk=pk)
        data = request.data.copy()
        data['user'] = coffee.user.id
        serializer = CoffeeSerializer(coffee, data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        coffee = serializer.save()
        return Response(CoffeeSerializer(coffee, context={'request': request}).data)

    def delete(self, request, pk):
        coffee = get_object_or_404(Coffee, pk=pk)
        coffee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OriginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        origins = Origin.objects.all()
        serializer = OriginSerializer(origins, many=True)
        return Response(serializer.data)


class FileUploadView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = UploadedFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        folder = os.path.join(settings.MEDIA_ROOT, 'uploads')
        files = os.listdir(folder)
        return Response({"files": files})


class UserList(APIView):
    """
    GET /api/users/ → admin only
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = AuthUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class OperationList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        operations = Operation.objects.select_related('user').all().order_by('-timestamp')
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)


@api_view(['GET'])
def debug_users_and_operations(request):
    users = AuthUser.objects.all()
    data = []
    for user in users:
        ops = Operation.objects.filter(user_id=user.id).order_by('timestamp')
        data.append({
            'id': user.id,
            'username': user.username,
            'operations': [op.operation for op in ops]
        })
    return Response(data)


@api_view(['GET'])
def debug_all_operations(request):
    data = [
        {
            'id': op.id,
            'user_id': op.user_id,
            'username': getattr(op.user, 'username', None),
            'operation': op.operation,
            'timestamp': op.timestamp.isoformat()
        }
        for op in Operation.objects.all().order_by('-timestamp')
    ]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_operation(request):
    user = request.user
    operation = request.data.get('operation')
    if not operation:
        return Response({'detail': 'Operation type required.'}, status=status.HTTP_400_BAD_REQUEST)
    Operation.objects.create(user=user, operation=operation)
    return Response({'detail': 'Operation logged.'}, status=status.HTTP_201_CREATED)
