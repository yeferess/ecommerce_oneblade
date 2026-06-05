from django.db import models

# AbstractUser es como una planilla que contiene parametros como username, email, firts_name
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    addres = models.TextField(blank=True)

    def __str__(self):
        return self.username
