from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    about = models.TextField(max_length=500, verbose_name='Расскажите о себе')
    avatar = models.ImageField(upload_to='users/', verbose_name='Ваше фото')
