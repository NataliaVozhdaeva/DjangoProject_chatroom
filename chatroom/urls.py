from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register-user'),
    path('login/', views.login_user, name='login-user'),
    path('logout/', views.logout_user, name='logout-user'),
    
    # Profile endpoints
    path('profile/', views.user_profile, name='user-profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    
    # Chat Room endpoints
    path('rooms/', views.list_rooms, name='list-rooms'),
    path('rooms/<int:room_id>/join/', views.join_room, name='join-room'),
    path('rooms/<int:room_id>/messages/', views.room_messages, name='room-messages'),
    path('rooms/<int:room_id>/participants/', views.room_participants, name='room-participants'),
]
