from rest_framework import serializers
from .models import User, ArtistProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError('the username should only contain alphanumeric characters')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class VerifyAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()


class ArtistProfileSerializer(serializers.ModelSerializer):
    su_status = serializers.ReadOnlyField()

    class Meta:
        model = ArtistProfile
        fields = ('id', 'bio', 'su_status','profile_picture')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.username
        token['su_status'] = user.is_superuser
        # ...

        return token


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    su_status = serializers.ReadOnlyField()

    class Meta:
        model = ArtistProfile
        fields = ('id','user', 'bio', 'profile_picture', 'su_status','followers', 'created_at', 'updated_at')