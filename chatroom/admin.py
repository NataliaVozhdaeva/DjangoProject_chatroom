from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, Room, Message, RoomParticipant


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'nickname')
    readonly_fields = ('created_at',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'content_preview', 'timestamp')
    list_filter = ('timestamp', 'room')
    search_fields = ('content', 'user__username', 'user__userprofile__nickname')
    readonly_fields = ('timestamp',)
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(RoomParticipant)
class RoomParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'joined_at')
    list_filter = ('joined_at', 'room')
    search_fields = ('user__username', 'user__userprofile__nickname', 'room__name')
    readonly_fields = ('joined_at',)
