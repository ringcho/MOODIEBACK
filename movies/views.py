import requests
import json
import pandas as pd
from ast import literal_eval
from collections import defaultdict
from decouple import config

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse

from .models import *
from .serializers import MovieListSerializer,MovieSerializer,CommentSerializer, ActorSerializer
# Create your views here.

TMDB_API_KEY = config('TMDB_API_KEY')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

def make_movie_db(request):
    movies_df = pd.read_csv('./movies/fixtures/tmdb_5000_movies.csv', usecols =['id','title','genres','vote_average', 'vote_count', 'keywords', 'overview'], skiprows=[i for i in range(2000,5000)])
    movies_df['genres'] = movies_df['genres'].apply(literal_eval)
    movies_df['keywords'] = movies_df['keywords'].apply(literal_eval)
    movies_df['genres'] = movies_df['genres'].apply(lambda x : [y['name'] for y in x])
    movies_df['keywords'] = movies_df['keywords'].apply(lambda x : [y['name'] for y in x])
    movies_df['keywords_literal'] = movies_df['keywords'].apply(lambda x: (' ').join(x))
    count_vect = CountVectorizer(min_df=0, ngram_range=(1,2))

    keyword_mat = count_vect.fit_transform(movies_df['keywords_literal'])
    keyword_sim = cosine_similarity(keyword_mat, keyword_mat)
    keyword_sim_sorted_ind = keyword_sim.argsort()[:,::-1]
    keyword_sim_df = pd.DataFrame(keyword_sim_sorted_ind)

    movies_df['keyword_sim'] = keyword_sim_df.apply(lambda x : [y for y in x][:20], axis=1)


    percentile = 0.6
    m = movies_df['vote_count'].quantile(percentile)  # 평점을 부여하기 위한 최소 평가 수
    C = movies_df['vote_average'].mean()  # 전체 영화의 평균 평점

    def weighted_vote_average(record):
        v = record['vote_count']  # 영화에 평가를 매긴 횟수
        R = record['vote_average']  # 영화의 평균 평점

        return ( (v/(v+m)) * R ) + ( (m/(m+v)) * C )  # 가중 평점 계산 식

    movies_df['weighted_vote'] = movies_df.apply(weighted_vote_average, axis=1)

    result = movies_df.to_json(orient='records')
    
    parsed = json.loads(result)

    for movie_json in parsed:
        movie_id = movie_json['id']
        movie_detail = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=ko-kr').json()

        movie = Movie (
            movie_id = movie_json['id'], 
            title = movie_json['title'],
            title_kr = movie_detail['title'],
            overview = movie_detail['overview'],
            release_date = movie_detail['release_date'], 
            backdrop_path=movie_detail['backdrop_path'],
            poster_path=movie_detail['poster_path'], 
            genres = movie_json['genres'],
            vote_average = movie_json['vote_average'],
            vote_count = movie_json['vote_count'],
            keywords = movie_json['keywords'],
            keyword_sim = movie_json['keyword_sim'],
            weighted_vote = movie_json['weighted_vote'],
            )
        movie.save()
        actor_r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=ko-Kr').json()['cast'][:6]
        crew_r = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=ko-Kr').json()['crew']
        for actor_data in actor_r:
            actor = Actor(
                id = actor_data['id'],
                name = actor_data['name'],
                character = actor_data['character'],
                profile_path = actor_data['profile_path']
                )
            actor.save()
            movie.actors.add(actor.id)
        for crew_data in crew_r:
            if crew_data['department'] == 'Directing':
                if crew_data['id']:
                    director = Director(
                        id = crew_data['id'],
                        name = crew_data['name'],
                        profile_path = crew_data['profile_path'],
                    )
                    director.save()
                    movie.directors.add(director.id)
                    break
    return JsonResponse(json.dumps(parsed))

@api_view(['GET'])
def movie_list(request):
    movies = get_list_or_404(Movie)
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def actor_list(request):
    actors = get_list_or_404(Actor)
    serializer = ActorSerializer(actors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    # actor = movie.actors.all()
    # print(actor)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def movie_comment(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.method =='DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def movie_like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    user = request.user
    if movie.likes.filter(pk=user.pk).exists():
        movie.likes.remove(user)
    else:
        movie.likes.add(user)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET','POST'])
def recommend(request):
    feelings = {
        ('느긋한','침착한','차분한','부드러운','평화로운','편안한','고요한'):'고요하고 편안한',
        ('황홀한','유쾌한','즐거운','기쁜','행복한'):'기쁘고 행복한',
        ('발랄한','기운 있는','활기찬','쾌활한'): '활기차고 활동적인',
        ('불안한','걱정스러운','신경질적인','긴장한'):'긴장되고 불안한',
        ('쓸쓸한','의기소침','울적한','상심한','외로운','기운없는','비참한','애처로운','슬픈','음울한'):'슬프고 우울한',
        ('흥분한','성난','짜증'):'화내고 적대적인',
        ('지루한','피곤한','지친','졸음이 오는','나태한','의심스러운','주저하는','산만한','멍해진'):'피곤하고 냉담한'
    }
    feelings_count = {
        '고요하고 편안한':0,
        '기쁘고 행복한':0,
        '활기차고 활동적인':0,
        '긴장되고 불안한':0,
        '슬프고 우울한':0,
        '화내고 적대적인':0,
        '피곤하고 냉담한':0,
    }
    recommed_genre = {
        '고요하고 편안한':["Documentary", "Drama", "Romance"],
        '기쁘고 행복한':["Romance","Action","Horror","Mystery","Thriller"],
        '활기차고 활동적인':["War","Western","Science Fiction"],
        '긴장되고 불안한':["Comedy","TV Movie","Music","Documentary"],
        '슬프고 우울한':["Animation","Comedy","Music"],
        '화내고 적대적인':["Comedy","Documentary"],
        '피곤하고 냉담한':["Comedy","TV Movie","Music"],
        
    }
    user = request.user
    # print(request.data)
    # print(request)
    for data in request.data['moods']:
        # print(data)
        for feel in feelings:
            if data in feel:
                feelings_count[feelings[feel]] += 1
        feeling = max(feelings_count, key=feelings_count.get)
        # print(feeling)
    genres_mood = recommed_genre[feeling]
    # print(genres)
    context  = defaultdict(list)
    for genre in genres_mood:
        movies = Movie.objects.all()
        for movie in movies:
            if genre in movie.genres:
                g = f'{genre}'
                if len(context[g])<=10:
                    context[g].append((movie.id,movie.weighted_vote))
    for recommend in context:
        context[recommend].sort(reverse=True, key= lambda x: x[1])
    # print(movies)
    # for movie in movies:
        # print(movie)
    return JsonResponse(context)