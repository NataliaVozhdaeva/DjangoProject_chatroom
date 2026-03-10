from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Room, Message, RoomParticipant


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['nickname']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    nickname = serializers.CharField(max_length=50, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'nickname']
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        nickname = validated_data.pop('nickname', None)
        password = validated_data.pop('password')
        password_confirm = validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        
        UserProfile.objects.create(
            user=user,
            nickname=nickname or user.username
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class RoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'is_private', 'created_by', 'created_at', 'participant_count']
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_nickname = serializers.CharField(source='user.userprofile.nickname', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'user_nickname', 'room', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']


class RoomParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_nickname = serializers.CharField(source='user.userprofile.nickname', read_only=True)
    
    class Meta:
        model = RoomParticipant
        fields = ['id', 'user', 'user_nickname', 'room', 'joined_at']
        read_only_fields = ['id', 'joined_at']
