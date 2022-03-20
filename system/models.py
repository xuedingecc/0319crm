from django.db import models
from datetime import datetime


class User(models.Model):
    username = models.CharField(max_length=20, null=True, db_column='user_name')
    password = models.CharField(max_length=100)
    truename = models.CharField(max_length=20, db_column='true_name')
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=20, null=True)
    is_valid = models.IntegerField(max_length=4, default=1)
    create_date = models.DateTimeField(default=datetime.now())
    update_date = models.DateTimeField(null=True)
    code = models.CharField(max_length=255, null=True)
    status = models.BooleanField(max_length=1)
    timestamp = models.CharField(max_length=255, null=True)
