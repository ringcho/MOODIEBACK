from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    profile_image = models.ImageField(upload_to="profile/images", blank=True, null=True)
    nickname = models.CharField(max_length=20, unique=True)