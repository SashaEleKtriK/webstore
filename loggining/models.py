from django.db import models
from django.contrib.auth.models import User

class Conf_code(models.Model):
    code = models.CharField(max_length=15)
    #user_id = models.IntegerField()
    is_actual = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
