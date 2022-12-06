from django.urls import path
from . import views

app_name = 'articles'
urlpatterns = [
    # article list / article create
    path('', views.article_c),
    path('<int:article_pk>/', views.article_rud),
    path('<int:article_pk>/like/', views.like_article),

    path('<int:article_pk>/comments/', views.comment_c),
    path('<int:article_pk>/comments/<int:comment_pk>/', views.comment_ud)
]
