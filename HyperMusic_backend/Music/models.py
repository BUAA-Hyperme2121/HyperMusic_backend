from django.db import models
from User.models import User
# Create your models here.



class Music(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Music_Creator')
    file_loc = models.CharField(max_length=100)
    likes = models.IntegerField()
    listen_time = models.IntegerField()
    #music_comments = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='Comment')
    #music_complains = models.ForeignKey(Complain, on_delete=models.CASCADE, related_name='Complain')
    music_front = models.ImageField()
    music_name = models.CharField(max_length=100)
    words = models.TextField()

    def add_listen_time(self):
        self.listen_time+=1
        self.save(update_fields="listen_time")



class MusicList(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    music_list_front = models.ImageField()
    music_list_profile = models.TextField()
    music = models.ManyToManyField(to=Music)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='MusicList_Creator')
    views = models.IntegerField()
    music_num = models.IntegerField(default=0)

    def add_music_num(self):
        self.music_num +=1
        self.save(update_fields="music_num")


class Label(models.Model):
    id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=100)
    label_music = models.ManyToManyField(to=Music)
    label_music_list = models.ManyToManyField(to=MusicList)

