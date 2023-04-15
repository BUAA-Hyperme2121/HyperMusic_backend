from django.db import models
from Music.models import Music
from User.models import User


# Create your models here.
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    music = models.ForeignKey(Music, on_delete=models.CASCADE,related_name="Comment_Music")
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Comment_Poster")



class Complain(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name="Complain_Music")
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Complain_Poster")
