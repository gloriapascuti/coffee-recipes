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
from django.db import models

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models.coffee import Coffee, Origin, Like
from .models.uploads import UploadedFile
from .models.coffee_operations import CoffeeOperation
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
        profile = user.userprofile
        if profile.users_operations:
            profile.users_operations += f",{operation}"
        else:
            profile.users_operations = operation
        profile.save()
    except Exception as e:
        print("Failed to log user operation:", e)


def log_coffee_operation(user, operation_type, coffee_id=None, coffee_name=None):
    """Log coffee operations to the CoffeeOperation table"""
    try:
        CoffeeOperation.objects.create(
            user=user,
            operation_type=operation_type,
            coffee_id=coffee_id,
            coffee_name=coffee_name
        )
    except Exception as e:
        print(f"Failed to log coffee operation: {e}")


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
        
        # Log the operation
        log_coffee_operation(request.user, 'add', coffee.id, coffee.name)
        
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
        
        # Log the operation
        log_coffee_operation(request.user, 'edit', coffee.id, coffee.name)
        
        return Response(CoffeeSerializer(coffee, context={'request': request}).data)

    def delete(self, request, pk):
        coffee = get_object_or_404(Coffee, pk=pk)
        coffee_name = coffee.name  # Store name before deletion
        coffee_id = coffee.id
        
        # Log the operation before deletion
        log_coffee_operation(request.user, 'delete', coffee_id, coffee_name)
        
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
        if not os.path.exists(folder):
            os.makedirs(folder)
        files = os.listdir(folder)
        return Response({"files": files})

    def delete(self, request, filename=None):
        if not filename:
            return Response(
                {"error": "Filename is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        
        if not os.path.exists(file_path):
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            os.remove(file_path)
            
            # Also remove from database if it exists
            try:
                uploaded_file = UploadedFile.objects.get(file__endswith=filename)
                uploaded_file.delete()
            except UploadedFile.DoesNotExist:
                pass  # File might not be in database, but that's okay
            
            return Response(
                {"message": f"File '{filename}' deleted successfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to delete file: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_ai_recipe(request):
    """Generate a coffee recipe using AI based on user attributes"""
    attributes = request.data.get('attributes', '')
    
    if not attributes:
        return Response(
            {'error': 'Attributes are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a prompt for the AI
    prompt = f"Give me a coffee recipe with Name, Origin and Description using these attributes: {attributes}"
    
    try:
        # For now, we'll create a simple mock response
        # In production, you would integrate with an actual AI service like OpenAI, Claude, or DeepSeek
        # 
        # Example integration with OpenAI:
        # import openai
        # openai.api_key = "your-api-key"
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # ai_generated_recipe = response.choices[0].message.content
        #
        # Example integration with DeepSeek:
        # import requests
        # headers = {
        #     'Authorization': f'Bearer {your_deepseek_api_key}',
        #     'Content-Type': 'application/json'
        # }
        # data = {
        #     'model': 'deepseek-chat',
        #     'messages': [{'role': 'user', 'content': prompt}]
        # }
        # response = requests.post('https://api.deepseek.com/v1/chat/completions', 
        #                         headers=headers, json=data)
        # ai_generated_recipe = response.json()['choices'][0]['message']['content']
        #
        # Example integration with Claude (Anthropic):
        # import anthropic
        # client = anthropic.Anthropic(api_key="your-api-key")
        # message = client.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     max_tokens=1000,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # ai_generated_recipe = message.content[0].text
        
        # Generate a simple response matching the requested format
        attributes_list = [attr.strip() for attr in attributes.split(',')]
        
        # Create a mock response in the format: Name, Origin, Description
        mock_recipe = f"""
**Name:** Custom {', '.join(attributes_list).title()} Blend

**Origin:** Ethiopian Highlands (Yirgacheffe region)

**Description:** A carefully crafted coffee that embodies {attributes} characteristics. This exceptional blend delivers a complex flavor profile featuring {', '.join(attributes_list)} notes, creating a memorable coffee experience. The beans are sourced from high-altitude farms and expertly roasted to highlight the unique {attributes} qualities you requested.
        """
        
        return Response({
            'recipe': mock_recipe,
            'attributes_used': attributes
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate recipe: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, coffee_id):
    """Toggle like/unlike for a coffee recipe"""
    try:
        coffee = Coffee.objects.get(id=coffee_id)
    except Coffee.DoesNotExist:
        return Response({'error': 'Coffee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    like, created = Like.objects.get_or_create(user=request.user, coffee=coffee)
    
    if not created:
        # Like already exists, so unlike it
        like.delete()
        liked = False
    else:
        # New like created
        liked = True
    
    return Response({
        'liked': liked,
        'likes_count': coffee.likes_count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def most_popular_recipes(request):
    """Get the 3 most liked coffee recipes"""
    # Get top 3 coffees by likes count, with a minimum of 1 like
    popular_coffees = Coffee.objects.annotate(
        total_likes=models.Count('likes')
    ).filter(
        total_likes__gt=0
    ).order_by('-total_likes')[:3]
    
    # If we don't have 3 liked recipes, fill with most recent recipes
    if len(popular_coffees) < 3:
        remaining_count = 3 - len(popular_coffees)
        popular_ids = [coffee.id for coffee in popular_coffees]
        
        # Get most recent recipes that aren't already in popular list
        recent_coffees = Coffee.objects.exclude(
            id__in=popular_ids
        ).order_by('-id')[:remaining_count]
        
        # Combine popular and recent
        popular_coffees = list(popular_coffees) + list(recent_coffees)
    
    serializer = CoffeeSerializer(popular_coffees, many=True, context={'request': request})
    return Response(serializer.data)
