from rest_framework import serializers
from .models import *

class MovieListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Movie
        fields = '__all__'

class ActorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        exclude = ['movies',]

class DirectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Director
        exclude = ['movies',]

class CommentSerializer(serializers.ModelSerializer):
    nickname = serializers.CharField(source='author.nickname', read_only=True)


    class Meta:
        model = Comment
        read_only_fields = ('movie','author')
        exclude = ['author',]


class MovieSerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    directors = DirectorSerializer(many=True, read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'