from django.db import models
from django.conf import settings
# Create your models here.


class Movie(models.Model):
    movie_id = models.IntegerField()
    title = models.CharField(max_length=100)
    title_kr = models.CharField(max_length=100)
    release_date = models.CharField(max_length=100)
    backdrop_path = models.CharField(max_length=100, null=True)
    poster_path = models.CharField(max_length=100, null=True)
    genres = models.JSONField()
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    overview = models.TextField(null=True)
    keywords = models.JSONField()
    keyword_sim = models.JSONField()
    weighted_vote = models.FloatField()
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL)


class Actor(models.Model):
    name = models.CharField(max_length=100)
    character = models.CharField(max_length=100)
    profile_path = models.CharField(max_length=100, null=True)
    movies = models.ManyToManyField(Movie, related_name='actors')


class Director(models.Model):
    name = models.CharField(max_length=100)
    profile_path = models.CharField(max_length=100, null=True)
    movies = models.ManyToManyField(Movie, related_name='directors')


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
