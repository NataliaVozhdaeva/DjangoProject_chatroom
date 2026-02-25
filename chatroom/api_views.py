from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer, UserSerializer
from .models import UserProfile


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user with username, email, and password.
    Also creates a UserProfile with nickname (defaults to username if not provided).
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        # Return user data without password
        response_serializer = UserSerializer(user)
        return Response({
            'message': 'User registered successfully',
            'user': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Get current user's profile information
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


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
