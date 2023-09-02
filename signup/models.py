from django.db import models

# Create your models here.

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length = 100,null=False)
    email = models.CharField(max_length = 100,null=False,unique=True)
    password = models.CharField(max_length = 100,null=False)
    verification_code = models.CharField(max_length=35)
    verified = models.BooleanField(default=False,null=False)

