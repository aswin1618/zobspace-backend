from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import RegisterSerializer, VerifyAccountSerializer, ArtistProfileSerializer, UserProfileSerializer
from rest_framework.response import Response
from .models import User, OTPVerification, ArtistProfile, Follow
from .emails import send_otp_via_mail
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404


# Create your views here.


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_otp_via_mail(serializer.data['email'])

        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        return Response({
            'status': 200,
            'message': 'registration successfull check email',
            'data': serializer.data,
        })


class OTPVerificationView(generics.CreateAPIView):

    def post(self, request):
        data = request.data
        serializer = VerifyAccountSerializer(data=data)
        if serializer.is_valid():
            email = serializer.data['email']
            otp_code = serializer.data['otp']
            user = User.objects.get(email=email)
        try:
            otp_verification = OTPVerification.objects.get(user=user)
        except OTPVerification.DoesNotExist:
            return Response({'message': 'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        if otp_verification.otp == otp_code and otp_verification.expiration_time > timezone.now():
            # OTP is valid
            user.is_verified = True
            user.save()
            otp_verification.delete()  # Delete the OTP verification entry after successful verification
            return Response({'message': 'OTP verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'OTP verification failed'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def update_profile(request):
    user = request.user
    artist_profile = user.artistprofile
    serializer = ArtistProfileSerializer(artist_profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def artistProfileView(request):
    user = request.user
    artist_profile = user.artistprofile
    serializer = ArtistProfileSerializer(artist_profile)
    data = serializer.data
    data['total_followers'] = artist_profile.total_followers()
    data['total_following'] = artist_profile.total_following()
    data['total_posts'] = artist_profile.total_posts()
    return Response(data)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def OtherArtistProfile(request):
    artist_id = request.data.get('artist_id')
    artist_profile = get_object_or_404(ArtistProfile, id=artist_id)
    serializer = ArtistProfileSerializer(artist_profile)
    data = serializer.data
    data['total_followers'] = artist_profile.total_followers()
    data['total_following'] = artist_profile.total_following()
    data['total_posts'] = artist_profile.total_posts()
    return Response(data)


@api_view(['POST'])
def follow_unfollow_artist(request):
    user = request.user
    artist_id = request.data.get('artist_id')

    if artist_id is None:
        return Response({'error': 'Artist ID is required.'}, status=HTTP_400_BAD_REQUEST)

    try:
        artist = ArtistProfile.objects.get(id=artist_id)
    except ArtistProfile.DoesNotExist:
        return Response({'error': 'Artist not found.'}, status=HTTP_400_BAD_REQUEST)

    try:
        follow = Follow.objects.get(follower=user, following=artist)
        follow.delete()
        message = 'Unfollowed the artist.'
    except Follow.DoesNotExist:
        follow = Follow.objects.create(follower=user, following=artist)
        message = 'Followed the artist.'

    return Response({'message': message}, status=HTTP_200_OK)


@api_view(['GET'])
def list_user_profiles(request):
    users = User.objects.exclude(is_superuser=True)
    profiles = ArtistProfile.objects.filter(user__in=users).exclude(user=request.user)
    serializer = UserProfileSerializer(profiles, many=True)
    profile_data = serializer.data
    for i, profile in enumerate(profiles):
        data = {
            'total_posts': profile.total_posts(),
            'total_followers': profile.total_followers(),
            'total_following': profile.total_following(),
        }
        profile_data[i].update(data)
    return Response(profile_data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_list_admin(request):
    profiles = ArtistProfile.objects.all()
    serializer = UserProfileSerializer(profiles, many=True)
    profile_data = serializer.data
    for i, profile in enumerate(profiles):
        data = {
            'total_posts': profile.total_posts(),
            'total_followers': profile.total_followers(),
            'total_following': profile.total_following(),
        }
        profile_data[i].update(data)
    return Response(profile_data, status=HTTP_200_OK)
