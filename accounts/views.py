from django.shortcuts import get_object_or_404,get_list_or_404
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views    import APIView

from .serializers import (
    ProfileSerializer,
    UserListSerializer
)

# Create your views here.

User = get_user_model()

@api_view(['GET'])
def profile(request, username):
    user = get_object_or_404(User, username=username)
    serializer = ProfileSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
def follow(request, username):
    user = get_object_or_404(User, username=username)
    serializer = ProfileSerializer(user)
    if request.user != user:
        if user.followers.filter(username=request.user.username).exists():
            user.followers.remove(request.user)
        else:
            user.followers.add(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_list(request):
    users = get_list_or_404(User)
    serializer = UserListSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def quit(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

