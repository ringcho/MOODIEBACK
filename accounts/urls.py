from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('profile/<str:username>/', views.profile),
    path('<str:username>/follow/', views.follow),
    path('userlist/', views.user_list),
    path('quit/<str:username>/',views.quit),
    # path('profile/update/<int:user_pk>/', views.profile_update),
    # path('register/', views.register),
]   