from django.db import models
from django.contrib.auth.models import User
import secrets

# Create your models here.


class MLState(models.Model):
    token=models.CharField(max_length=255, default=secrets.token_hex())
    created=models.DateTimeField(auto_now_add=True)


class MLToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    ml_user_id = models.IntegerField(default=0)
    access_token = models.CharField(max_length=255, default="-")
    refresh_token = models.CharField(max_length=255, default="-")
