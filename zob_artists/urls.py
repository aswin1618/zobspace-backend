from django.urls import path
from .views import RegisterView, OTPVerificationView, update_profile, artistProfileView, list_user_profiles, \
    follow_unfollow_artist, OtherArtistProfile, user_list_admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
    
urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('verify_otp', OTPVerificationView.as_view(), name='otp_verification'),

    path('profile/', artistProfileView, name='artist_profile'),
    path('update_profile/', update_profile, name='update_profile'),

    path('user_profiles/', list_user_profiles, name='list_user_profiles'),
    path('artist_profile/', OtherArtistProfile, name='artist_profile'),
    path('follow/', follow_unfollow_artist, name='follow_unfollow_artist'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user_list_admin', user_list_admin, name='user_list_admin'),
]
