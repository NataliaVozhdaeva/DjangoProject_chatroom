from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserSerializer, RoomSerializer, MessageSerializer, RoomParticipantSerializer
from .models import UserProfile, Room, Message, RoomParticipant


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
@csrf_exempt
def register_user(request):
    """
    Register a new user with username, email, and password.
    Also creates a UserProfile with nickname (defaults to username if not provided).
    """
    print("Request data:", request.data)  # Debug print
    print("Request method:", request.method)  # Debug print
    
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        # Create or get token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data and token
        response_serializer = UserSerializer(user)
        return Response({
            'message': 'User registered successfully',
            'user': response_serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@authentication_classes([])
@csrf_exempt
def login_user(request):
    """
    Login user using Django session authentication
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        if user.is_active:
            # Create or get token for the user
            token, created = Token.objects.get_or_create(user=user)
            user_serializer = UserSerializer(user)
            return Response({
                'message': 'Login successful',
                'user': user_serializer.data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'User account is disabled'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """
    Logout user by deleting their auth token
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Get current user's profile information
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# Chat Room Views
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def list_rooms(request):
    """
    List all public chat rooms (GET) or create a new room (POST)
    """
    if request.method == 'GET':
        rooms = Room.objects.all().order_by('-created_at')
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RoomSerializer(data=request.data)
        
        if serializer.is_valid():
            room = serializer.save(created_by=request.user)
            
            # Automatically add the creator as a participant
            RoomParticipant.objects.create(user=request.user, room=room)
            
            response_serializer = RoomSerializer(room)
            return Response({
                'message': 'Room created successfully',
                'room': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_room(request, room_id):
    """
    Join a public chat room
    """
    try:
        room = Room.objects.get(id=room_id)
        
        # Check if user is already a participant
        if RoomParticipant.objects.filter(user=request.user, room=room).exists():
            return Response({
                'error': 'You are already a participant in this room'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add user as participant
        RoomParticipant.objects.create(user=request.user, room=room)
        
        return Response({
            'message': 'Joined room successfully'
        }, status=status.HTTP_200_OK)
        
    except Room.DoesNotExist:
        return Response({
            'error': 'Room not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def room_messages(request, room_id):
    """
    Get all messages (GET) or send a message (POST) in a room
    """
    try:
        room = Room.objects.get(id=room_id)
        
        # Check if user is a participant
        if not RoomParticipant.objects.filter(user=request.user, room=room).exists():
            return Response({
                'error': 'You are not a participant in this room'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'GET':
            messages = Message.objects.filter(room=room).order_by('timestamp')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            content = request.data.get('content')
            if not content:
                return Response({
                    'error': 'Message content is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            message = Message.objects.create(
                content=content,
                user=request.user,
                room=room
            )
            
            serializer = MessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Room.DoesNotExist:
        return Response({
            'error': 'Room not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def room_participants(request, room_id):
    """
    Get all participants in a room
    """
    try:
        room = Room.objects.get(id=room_id)
        
        # Check if user is a participant
        if not RoomParticipant.objects.filter(user=request.user, room=room).exists():
            return Response({
                'error': 'You are not a participant in this room'
            }, status=status.HTTP_403_FORBIDDEN)
        
        participants = RoomParticipant.objects.filter(room=room).order_by('joined_at')
        serializer = RoomParticipantSerializer(participants, many=True)
        return Response(serializer.data)
        
    except Room.DoesNotExist:
        return Response({
            'error': 'Room not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    """
    Update current user's profile information
    """
    user = request.user
    profile = user.userprofile
    
    # Update user fields
    if 'email' in request.data:
        if User.objects.filter(email=request.data['email']).exclude(id=user.id).exists():
            return Response(
                {'email': 'A user with this email already exists.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.email = request.data['email']
    
    if 'first_name' in request.data:
        user.first_name = request.data['first_name']
    if 'last_name' in request.data:
        user.last_name = request.data['last_name']
    
    # Update profile fields
    if 'nickname' in request.data:
        if UserProfile.objects.filter(nickname=request.data['nickname']).exclude(id=profile.id).exists():
            return Response(
                {'nickname': 'A user with this nickname already exists.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        profile.nickname = request.data['nickname']
    
    user.save()
    profile.save()
    
    serializer = UserSerializer(user)
    return Response({
        'message': 'Profile updated successfully',
        'user': serializer.data
    })
