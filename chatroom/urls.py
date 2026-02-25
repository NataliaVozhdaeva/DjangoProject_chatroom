from django.urls import path
from . import api_views

urlpatterns = [
    path('register/', api_views.register_user, name='register-user'),
    path('profile/', api_views.user_profile, name='user-profile'),
    path('profile/update/', api_views.update_profile, name='update-profile'),
]
