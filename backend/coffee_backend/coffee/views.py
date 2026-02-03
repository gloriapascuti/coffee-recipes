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

from .models.coffee import Coffee, Origin, Like, ConsumedCoffee
from .models.health import UserHealthProfile, BloodPressureEntry
from .models.uploads import UploadedFile
from .models.coffee_operations import CoffeeOperation
from .models.challenges import Challenge, ChallengeRecipe, Vote, Notification
from .serializers import (
    CoffeeSerializer,
    OriginSerializer,
    UploadedFileSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    AuthUserSerializer,
    OperationSerializer,
    ChallengeSerializer,
    ChallengeRecipeSerializer,
    VoteSerializer,
    NotificationSerializer,
    ConsumedCoffeeSerializer,
    UserHealthProfileSerializer,
    BloodPressureEntrySerializer,
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


# Challenge System Views

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def challenge_list(request):
    """Get all challenges or create a new challenge"""
    if request.method == 'GET':
        challenges = Challenge.objects.select_related(
            'challenger', 'challenged', 'winner'
        ).prefetch_related('recipes', 'votes').all().order_by('-created_at')
        
        serializer = ChallengeSerializer(challenges, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        challenged_username = request.data.get('challenged_username')
        coffee_type = request.data.get('coffee_type')
        
        if not challenged_username or not coffee_type:
            return Response(
                {'error': 'challenged_username and coffee_type are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import CustomUser
            challenged_user = CustomUser.objects.get(username=challenged_username)
        except CustomUser.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if challenged_user == request.user:
            return Response(
                {'error': 'You cannot challenge yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if challenged_user.is_banned:
            return Response(
                {'error': 'Cannot challenge banned users'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is already in an active challenge
        active_statuses = ['pending', 'accepted', 'active', 'voting']
        existing_challenge = Challenge.objects.filter(
            models.Q(challenger=challenged_user) | models.Q(challenged=challenged_user),
            status__in=active_statuses
        ).exists()
        
        if existing_challenge:
            return Response(
                {'error': 'User is already in an active challenge'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        challenge = Challenge.objects.create(
            challenger=request.user,
            challenged=challenged_user,
            coffee_type=coffee_type
        )
        
        # Create notification for challenged user
        Notification.objects.create(
            user=challenged_user,
            notification_type='challenge',
            message=f'{request.user.username} challenged you to create a {coffee_type} recipe!',
            challenge=challenge
        )
        
        serializer = ChallengeSerializer(challenge, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_to_challenge(request, challenge_id):
    """Accept or decline a challenge"""
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if challenge.challenged != request.user:
        return Response(
            {'error': 'You can only respond to challenges directed at you'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if challenge.status != 'pending':
        return Response(
            {'error': 'Challenge is no longer pending'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    response = request.data.get('response')  # 'accept' or 'decline'
    
    if response == 'accept':
        challenge.status = 'accepted'
        challenge.accepted_at = timezone.now()
        challenge.save()
        
        # Create notifications
        Notification.objects.create(
            user=challenge.challenger,
            notification_type='challenge_accepted',
            message=f'{request.user.username} accepted your challenge! Submit your recipe.',
            challenge=challenge
        )
        
    elif response == 'decline':
        challenge.status = 'declined'
        challenge.save()
        
        # Create notification
        Notification.objects.create(
            user=challenge.challenger,
            notification_type='challenge_declined',
            message=f'{request.user.username} declined your challenge.',
            challenge=challenge
        )
        
    else:
        return Response(
            {'error': 'Response must be either "accept" or "decline"'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ChallengeSerializer(challenge, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_recipe(request, challenge_id):
    """Submit a recipe for a challenge"""
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user not in [challenge.challenger, challenge.challenged]:
        return Response(
            {'error': 'You are not a participant in this challenge'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    if challenge.status != 'accepted':
        return Response(
            {'error': 'Challenge must be accepted before submitting recipes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already submitted a recipe
    if ChallengeRecipe.objects.filter(challenge=challenge, user=request.user).exists():
        return Response(
            {'error': 'You have already submitted a recipe for this challenge'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = ChallengeRecipeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        recipe = serializer.save(challenge=challenge, user=request.user)
        
        # Check if both users have submitted recipes
        if challenge.recipes.count() == 2:
            challenge.status = 'voting'
            challenge.save()
            
            # Notify both participants that voting has started
            for user in [challenge.challenger, challenge.challenged]:
                Notification.objects.create(
                    user=user,
                    notification_type='voting_started',
                    message=f'Both recipes are submitted! Voting has started for the {challenge.coffee_type} challenge.',
                    challenge=challenge
                )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_challenge(request, challenge_id):
    """Vote for a recipe in a challenge"""
    try:
        challenge = Challenge.objects.get(id=challenge_id)
    except Challenge.DoesNotExist:
        return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if challenge.status != 'voting':
        return Response(
            {'error': 'Challenge is not in voting phase'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user is a participant (participants can't vote)
    if request.user in [challenge.challenger, challenge.challenged]:
        return Response(
            {'error': 'Challenge participants cannot vote'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if user already voted
    if Vote.objects.filter(challenge=challenge, voter=request.user).exists():
        return Response(
            {'error': 'You have already voted in this challenge'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    voted_for_username = request.data.get('voted_for')
    
    try:
        from users.models import CustomUser
        voted_for_user = CustomUser.objects.get(username=voted_for_username)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if voted_for_user not in [challenge.challenger, challenge.challenged]:
        return Response(
            {'error': 'You can only vote for challenge participants'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    vote = Vote.objects.create(
        challenge=challenge,
        voter=request.user,
        voted_for=voted_for_user
    )
    
    # Check if we have enough votes to determine a winner
    total_users = CustomUser.objects.count()
    total_votes = challenge.total_votes
    challenger_votes = challenge.challenger_votes
    challenged_votes = challenge.challenged_votes
    
    # Winner needs more than half of total users to vote for them
    required_votes = (total_users // 2) + 1
    
    winner = None
    if challenger_votes >= required_votes:
        winner = challenge.challenger
    elif challenged_votes >= required_votes:
        winner = challenge.challenged
    
    if winner:
        challenge.status = 'completed'
        challenge.winner = winner
        challenge.completed_at = timezone.now()
        challenge.save()
        
        # Find the winning recipe and add it to main coffee list with star
        winning_recipe = ChallengeRecipe.objects.get(challenge=challenge, user=winner)
        # Create the coffee with star emoji in the name
        winner_votes = challenge.challenger_votes if winner == challenge.challenger else challenge.challenged_votes
        new_coffee = Coffee.objects.create(
            name=f"⭐ {winning_recipe.name}",
            origin=winning_recipe.origin,
            description=winning_recipe.description,
            user=winner,
            is_community_winner=True
        )
        
        # Create likes from all the voters who voted for this winner
        winning_votes = Vote.objects.filter(challenge=challenge, voted_for=winner)
        for vote in winning_votes:
            Like.objects.create(coffee=new_coffee, user=vote.voter)
        
        # Create notifications
        Notification.objects.create(
            user=winner,
            notification_type='challenge_won',
            message=f'Congratulations! You won the {challenge.coffee_type} challenge!',
            challenge=challenge
        )
        
        loser = challenge.challenger if winner == challenge.challenged else challenge.challenged
        Notification.objects.create(
            user=loser,
            notification_type='challenge_lost',
            message=f'You lost the {challenge.coffee_type} challenge. Better luck next time!',
            challenge=challenge
        )
    
    serializer = ChallengeSerializer(challenge, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    """Get notifications for the current user"""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related('challenge').order_by('-created_at')
    
    serializer = NotificationSerializer(notifications, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_users(request):
    """Get users that can be challenged (not currently in active challenges and not banned)"""
    from users.models import CustomUser
    from users.serializers import UserSerializer
    
    active_statuses = ['pending', 'accepted', 'active', 'voting']
    
    # Get users who are currently in active challenges
    busy_user_ids = set()
    active_challenges = Challenge.objects.filter(status__in=active_statuses)
    for challenge in active_challenges:
        busy_user_ids.add(challenge.challenger.id)
        busy_user_ids.add(challenge.challenged.id)
    
    # Get all users except current user, busy users, and banned users
    available_users = CustomUser.objects.exclude(
        models.Q(id=request.user.id) | 
        models.Q(id__in=busy_user_ids) |
        models.Q(is_banned=True)
    ).order_by('username')
    
    serializer = UserSerializer(available_users, many=True)
    return Response(serializer.data)


# Consumed Coffee Endpoints

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_consumed_coffee(request, coffee_id):
    """Add a coffee to user's consumed list"""
    try:
        coffee = Coffee.objects.get(id=coffee_id)
    except Coffee.DoesNotExist:
        return Response({'error': 'Coffee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    consumed_coffee = ConsumedCoffee.objects.create(user=request.user, coffee=coffee)
    serializer = ConsumedCoffeeSerializer(consumed_coffee, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_consumed_coffee(request, consumed_id):
    """Remove a consumed coffee entry"""
    try:
        consumed_coffee = ConsumedCoffee.objects.get(id=consumed_id, user=request.user)
        consumed_coffee.delete()
        return Response({'message': 'Consumed coffee removed'}, status=status.HTTP_200_OK)
    except ConsumedCoffee.DoesNotExist:
        return Response({'error': 'Consumed coffee not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_consumed_coffees(request):
    """Get consumed coffees organized by time periods"""
    from datetime import datetime, timedelta
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_ago = today_start - timedelta(days=7)
    month_ago = today_start - timedelta(days=30)
    
    # Get all consumed coffees for user
    all_consumed = ConsumedCoffee.objects.filter(user=request.user).select_related('coffee').order_by('-consumed_at')
    
    # Organize by periods
    today = [ConsumedCoffeeSerializer(cc, context={'request': request}).data 
             for cc in all_consumed if cc.consumed_at >= today_start]
    yesterday = [ConsumedCoffeeSerializer(cc, context={'request': request}).data 
                 for cc in all_consumed if yesterday_start <= cc.consumed_at < today_start]
    last_7_days = [ConsumedCoffeeSerializer(cc, context={'request': request}).data 
                   for cc in all_consumed if cc.consumed_at >= week_ago and cc.consumed_at < today_start]
    last_month = [ConsumedCoffeeSerializer(cc, context={'request': request}).data 
                  for cc in all_consumed if cc.consumed_at >= month_ago and cc.consumed_at < today_start]
    
    return Response({
        'today': today,
        'yesterday': yesterday,
        'last_7_days': last_7_days,
        'last_month': last_month,
        'all': ConsumedCoffeeSerializer(all_consumed, many=True, context={'request': request}).data
    })


# Health Profile Endpoints

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def health_profile(request):
    """Get or update user health profile"""
    profile, created = UserHealthProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserHealthProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserHealthProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_blood_pressure(request):
    """Add a blood pressure reading"""
    serializer = BloodPressureEntrySerializer(data=request.data)
    if serializer.is_valid():
        bp_entry = serializer.save(user=request.user)
        return Response(BloodPressureEntrySerializer(bp_entry).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_blood_pressure_entries(request):
    """Get user's blood pressure entries"""
    entries = BloodPressureEntry.objects.filter(user=request.user).order_by('-measured_at')
    serializer = BloodPressureEntrySerializer(entries, many=True)
    return Response(serializer.data)


# Prediction Endpoint

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_prediction(request):
    """Generate heart disease risk prediction based on consumed coffees and health profile"""
    from datetime import datetime, timedelta
    
    period = request.data.get('period', 'week')  # week, month, year
    # Optional BP override for this prediction
    systolic = request.data.get('systolic')
    diastolic = request.data.get('diastolic')
    pulse = request.data.get('pulse')
    
    # Calculate time range
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        return Response({'error': 'Invalid period. Use: week, month, or year'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Get consumed coffees in period
    consumed_coffees = ConsumedCoffee.objects.filter(
        user=request.user,
        consumed_at__gte=start_date
    ).select_related('coffee')
    
    # Calculate caffeine features
    total_caffeine = sum(cc.coffee.get_caffeine_mg() for cc in consumed_coffees)
    avg_daily_caffeine = total_caffeine / max((now - start_date).days, 1)
    num_coffees = consumed_coffees.count()
    
    # Get health profile
    try:
        health_profile = request.user.health_profile
    except UserHealthProfile.DoesNotExist:
        health_profile = None
    
    # Get latest BP (use override if provided, otherwise latest entry)
    bp_entry = None
    if systolic and diastolic:
        # Use provided BP
        bp_entry = {
            'systolic': systolic,
            'diastolic': diastolic,
            'pulse': pulse
        }
    else:
        # Get latest BP entry
        latest_bp = BloodPressureEntry.objects.filter(user=request.user).order_by('-measured_at').first()
        if latest_bp:
            bp_entry = {
                'systolic': latest_bp.systolic,
                'diastolic': latest_bp.diastolic,
                'pulse': latest_bp.pulse,
                'measured_at': latest_bp.measured_at
            }
    
    # For now, return a mock prediction
    # TODO: Integrate actual ML model
    risk_probability = 0.15  # Placeholder
    if health_profile:
        # Simple heuristic based on health factors
        if health_profile.has_hypertension:
            risk_probability += 0.1
        if health_profile.has_diabetes:
            risk_probability += 0.1
        if health_profile.has_family_history_chd:
            risk_probability += 0.05
        if health_profile.is_smoker:
            risk_probability += 0.1
        if avg_daily_caffeine > 400:  # High caffeine
            risk_probability += 0.05
    
    # Clamp between 0 and 1
    risk_probability = min(max(risk_probability, 0.0), 1.0)
    
    # Determine risk category
    if risk_probability < 0.2:
        risk_category = 'low'
    elif risk_probability < 0.5:
        risk_category = 'moderate'
    else:
        risk_category = 'high'
    
    # Check missing fields
    missing_fields = []
    if not health_profile:
        missing_fields = ['health_profile']
    else:
        if not health_profile.sex:
            missing_fields.append('sex')
        if not health_profile.date_of_birth:
            missing_fields.append('date_of_birth')
        if not health_profile.height_cm:
            missing_fields.append('height_cm')
        if not health_profile.weight_kg:
            missing_fields.append('weight_kg')
    
    return Response({
        'period': period,
        'risk_probability': round(risk_probability, 3),
        'risk_percentage': round(risk_probability * 100, 1),
        'risk_category': risk_category,
        'caffeine_stats': {
            'total_mg': round(total_caffeine, 2),
            'avg_daily_mg': round(avg_daily_caffeine, 2),
            'num_coffees': num_coffees
        },
        'used_bp': bp_entry,
        'missing_fields': missing_fields,
        'note': 'This is a preliminary prediction. A trained ML model will be integrated for accurate risk assessment.'
    })
