from django.db import models
from django.contrib.auth.models import User


class Invite(models.Model):
    token = models.CharField(max_length=256, verbose_name='Activation key')
    is_used = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
