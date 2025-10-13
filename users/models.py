from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    location = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.username