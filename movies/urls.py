from django.urls import path
from . import views

urlpatterns = [
    path('makeDB/', views.make_movie_db),
    path('recommend/',views.recommend),
    path('',views.movie_list),
    path('<int:movie_pk>/',views.movie_detail),
    path('comment/<int:movie_pk>/', views.movie_comment),
    path('comment/detail/<int:comment_pk>/', views.comment_detail),
    path('likes/<int:movie_pk>/', views.movie_like),
    path('actors/', views.actor_list),
]
