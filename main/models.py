from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.user)

class Event(models.Model):
    code_name = models.SlugField(unique=True, max_length=50)
    title = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_Date = models.DateTimeField()
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    def __str__(self):
        return self.title + " at " + str(self.start_date) + " to " + str(self.end_Date) + " created by " + str(self.creator)