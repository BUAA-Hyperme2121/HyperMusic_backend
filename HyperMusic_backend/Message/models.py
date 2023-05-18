from django.db import models
from Music.models import Music
from User.models import User


# Create your models here.
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(verbose_name='评论音乐id', null=False)
    poster_id = models.IntegerField(verbose_name='评论发布者id', default=-1)
    content = models.TextField()
    #0 是音乐 1 是歌单 2 是动态
    type = models.IntegerField(verbose_name='评论种类')

    likes = models.IntegerField(verbose_name='点赞数')

    def to_dic(self):
        return {
            "id": self.id,
            "type": self.type,
            "create_date": self.create_date,
            "music_id": self.music_id,
            "poster_id": self.poster_id,
            "content": self.content,
            "likes": self.likes,
            "type": self.type,
        }

    def add_like(self):
        self.likes += 1
        self.save(update_fields="likes")


class Complain(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(verbose_name='投诉对象id', default=-1)
    poster_id = models.IntegerField(verbose_name='投诉发表者id', default=-1)
    content = models.TextField()
    #投诉种类 0 为歌曲 1为歌单
    type = models.IntegerField(verbose_name='评论种类')
    #0 未审核 1 通过审核 2未通过
    state = models.IntegerField(verbose_name='状态')

    def to_dic(self):
        return {
            "id": self.id,
            "create_date": self.create_date,
            "music_id": self.music_id,
            "poster_id": self.poster_id,
            "content": self.content,
            "type": self.type,
            "state": self.state,
        }


#用户间的私信
class Message(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField('标题', max_length=32)
    poster_id = models.IntegerField(verbose_name='发送私信者的id', default=0)
    receiver_id = models.IntegerField(verbose_name='收到私信者的id', default=0)
    content = models.TextField(verbose_name='私信内容')
    cre_date = models.DateTimeField(auto_now_add=True)
    #0 - 未读 1 - 已读
    is_read = models.IntegerField(verbose_name="读状态")



    def __str__(self):
        return '站内信' + self.title


    def to_dic(self):
        return {
            "title" :self.title,
            "receiver_id": self.receiver_id,
            "poster_id": self.poster_id,
            "content": self.content,
            "cre_date": self.cre_date
        }


class VerifyCode(models.Model):

    id = models.AutoField(primary_key=True)
    num = models.IntegerField(verbose_name="验证码内容")
    cre_date = models.DateTimeField(auto_now_add=True)
    email = models.CharField(max_length=32)

    def to_dic(self):
        return {

            "num": self.num,
            "cre_date": self.cre_date,
            "user_id": self.user_id,
        }


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('标题', max_length=32)
    poster_id = models.IntegerField(verbose_name='发送私信者的id', default=0)
    content = models.TextField(verbose_name='私信内容')
    cre_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(verbose_name='点赞数')

    def add_like(self):
        self.likes += 1
        self.save(update_fields="likes")

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


class UserToMessage(models.Model):
    user_id = models.IntegerField(verbose_name='用户 主体', default=0)
    message_id = models.IntegerField(verbose_name='消息', default=0)


class PostToComment(models.Model):
    post_id = models.IntegerField(verbose_name='音乐主体', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)


class MusicListToComment(models.Model):
    musiclist_id = models.IntegerField(verbose_name='音乐主体', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)




class MusicListToComplain(models.Model):
    musiclist_id = models.IntegerField(verbose_name='音乐主体', default=0)
    complain_id = models.IntegerField(verbose_name='评论', default=0)
