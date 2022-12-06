from rest_framework import serializers
from django.contrib.auth import get_user_model
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
from movies.models import Movie

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    profile_image = serializers.ImageField(
        allow_empty_file=True,
        required=False,
    )
    nickname = serializers.CharField(
        max_length=20,
    )
    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict['nickname'] = self.validated_data.get('nickname', '')
        data_dict['profile_image'] = self.validated_data.get('profile_image', '')
        return data_dict

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'nickname', 'profile_image','username')
        read_only_fields = ('id', 'email',)

# 사용자 프로필에 들어가는 정보
class ProfileSerializer(serializers.ModelSerializer):

    class MovieSerializer(serializers.ModelSerializer):
        likes = serializers.StringRelatedField(many=True,read_only=True)

        class Meta:
            model = Movie
            fields = ('pk','title_kr','poster_path','keyword_sim','likes','weighted_vote')

    movie_set = MovieSerializer(many=True, read_only=True)
    followers = serializers.StringRelatedField(many=True, read_only=True)
    followings = serializers.StringRelatedField(many=True, read_only=True)
    # profileImage = serializers.ImageField(use_url=True)

    class Meta:
        model = User
        fields = ('id','username','movie_set','followings','followers', 'profile_image', 'nickname')

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk','nickname','username','followings','followers',)