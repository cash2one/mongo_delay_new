from django.db import models

# Create your models here.
class user_info(models.Model):
    username = models.CharField(max_length=64)
    passwd = models.CharField(max_length=32)
    ctime = models.DateTimeField()
    def __str__(self):
        return self.username