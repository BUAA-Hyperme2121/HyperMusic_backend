from django.db import models
from Music.models import Music
from User.models import User


# Create your models here.
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    music_id = models.IntegerField(verbose_name='评论音乐id', default=-1)
    poster_id = models.IntegerField(verbose_name='评论发布者id', default=-1)
    content = models.TextField()


    def to_dic(self):
        return {
            'id':self.id,
            'create_date':self.create_date,
            'music_id':self.music_id,
            'poster_id':self.poster_id,
            'content':self.content,
        }


class Complain(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    music_id = models.IntegerField(verbose_name='投诉音乐id', default=-1)
    poster_id = models.IntegerField(verbose_name='投诉发表者id', default=-1)
    content = models.TextField()


    def to_dic(self):
        return {
            'id':self.id,
            'create_date':self.create_date,
            'music_id':self.music_id,
            'poster_id':self.poster_id,
            'content':self.content,
        }

class UserToComment(models.Model):
    user_id = models.IntegerField(verbose_name='用户 主体', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)


class UserToComplain(models.Model):
    user_id = models.IntegerField(verbose_name='用户 主体', default=0)
    complain_id = models.IntegerField(verbose_name='评论', default=0)


class MusicToComplain(models.Model):
    music_id = models.IntegerField(verbose_name='音乐主体', default=0)
    complain_id = models.IntegerField(verbose_name='评论', default=0)


class MusicToComment(models.Model):
    music_id = models.IntegerField(verbose_name='音乐主体', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)


