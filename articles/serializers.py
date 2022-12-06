from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Article, Comment


User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username','nickname')

    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('pk', 'user', 'content', 'article', 'created_at', 'updated_at',)
        read_only_fields = ('article', )


# 단일 게시글 정보
class ArticleSerializer(serializers.ModelSerializer):
    
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ('pk', 'username', 'nickname', 'profile_image')

    comments = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    like_users = UserSerializer(read_only=True, many=True)

    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.CharField(source='user.profile_image', read_only=True)
    
    class Meta:
        model = Article
        fields = ('pk', 'user', 'nickname', 'profile_image', 'title', 'content', 'comments', 'created_at', 'updated_at', 'like_users', 'like_count', 'comment_count',)


# 게시글 목록
class ArticleListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    profile_image = serializers.CharField(source='user.profile_image', read_only=True)
    class Meta:
        model = Article
        # fields = ('id', 'title', 'content')
        fields = ('id', 'title', 'content', 'user', 'username', 'nickname', 'profile_image')