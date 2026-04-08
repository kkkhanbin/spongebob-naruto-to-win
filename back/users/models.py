from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email'] # Обязательные поля при создании через консоль
