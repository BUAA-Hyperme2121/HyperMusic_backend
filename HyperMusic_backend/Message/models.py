from django.db import models
from Music.models import Music
from User.models import User


# Comments-0 Complains-1 Post-2

# Create your models here.
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    # 1-歌曲 2- 歌单 3 - 动态
    object_id = models.IntegerField(verbose_name='评论音乐id', null=False)
    poster_id = models.IntegerField(verbose_name='评论发布者id', default=-1)
    content = models.TextField()
    # 1-歌曲 2- 歌单 3 - 动态
    type = models.IntegerField(verbose_name='评论种类')

    like_num = models.IntegerField(verbose_name='点赞数', default=0)
    reply_num = models.IntegerField(verbose_name="回复数", default=0)

    def to_dic(self):
        return {
            "id": self.id,
            "type": self.type,
            "create_date": self.create_date,
            "object_id": self.object_id,
            "poster_id": self.poster_id,
            "content": self.content,
            "likes": self.like_num,
            "like_num": self.like_num,
            "reply_num":self.reply_num,

        }


    def add_like(self):
        self.like_num += 1
        self.save(update_fields="like_num")


class Complain(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(verbose_name='投诉对象id', default=-1)
    poster_id = models.IntegerField(verbose_name='投诉发表者id', default=-1)
    content = models.TextField()
    #投诉种类 1 为歌曲 2为歌单
    type = models.IntegerField(verbose_name='评论种类')
    # 1 审核中 2审核完成
    state = models.IntegerField(verbose_name='审核状态')
    # 审核完成时间
    audit_time = models.DateTimeField(blank=True)
    #result: 1 -成功 2 -失败
    result = models.IntegerField(verbose_name="审核结果", blank=True)
    #失败原因
    reason = models.TextField(verbose_name="失败原因", blank=True)
    title = models.CharField(max_length=200)


    def to_dic(self):
        return {
            "id": self.id,
            "create_date": self.create_date,
            "object_id": self.object_id,
            "poster_id": self.poster_id,
            "type": self.type,
            "state": self.state,
            "title":self.title,
            "result": self.result,

        }
    def to_dic_detail(self):
        return {
            "id": self.id,
            "create_date": self.create_date,
            "object_id": self.object_id,
            "poster_id": self.poster_id,
            "type": self.type,
            "state": self.state,
            "title": self.title,
            "result": self.result,
            "reason": self.reason,
            "audit_time": self.audit_time,
            "content": self.content,
        }

#用户间的私信
class Message(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField('标题', max_length=32)
    poster_id = models.IntegerField(verbose_name='发送私信者的id', default=0)
    receiver_id = models.IntegerField(verbose_name='收到私信者的id', default=0)
    content = models.TextField(verbose_name='私信内容')
    create_date = models.DateTimeField(auto_now_add=True)
    object_id = models.IntegerField(verbose_name="消息对应的对象id", blank=True)
    #1-歌曲 2- 歌单 3 - 动态
    type = models.IntegerField(verbose_name="消息对应的对象种类", blank=True)
    # 1 评论 2 点赞 3 关注 4 投诉 5 系统消息
    message_type = models.IntegerField(verbose_name="消息种类")
    #0 - 未读 1 - 已读
    state = models.IntegerField(verbose_name="读状态", default=0)



    def __str__(self):
        return '站内信' + self.title


    def to_dic(self):
        return {
            "id":self.id,
            "title" :self.title,
            "receiver_id": self.receiver_id,
            "poster_id": self.poster_id,
            "content": self.content,
            "create_date": self.create_date,
            "object_id":self.object_id,
            "type":self.type,
            "state":self.state,
            "message_type":self.message_type,
        }


    def to_dic_detail(self):
        return {}


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
    poster_id = models.IntegerField(verbose_name='发送私信者的id', default=0)
    content = models.TextField(verbose_name='私信内容')
    create_date = models.DateTimeField(auto_now_add=True)
    like_num = models.IntegerField(verbose_name='点赞数', default=0)
    comment_num = models.IntegerField(verbose_name='评论数', default=0)
    #type：1 - 歌曲 2 - 歌单 0 -不含对象
    type = models.IntegerField(verbose_name="分享对象的种类")
    object_id = models.IntegerField(verbose_name="分享对象的id")


    def to_dic(self):
        return {
            "id":self.id,
            "title":self.title,
            "poster_id":self.poster_id,
            "content":self.content,
            "create_date":self.create_date,
            "like_num":self.like_num,
            "comment_num":self.comment_num,
            "type":self.type,
            "object_id":self.object_id,
        }


    def add_like(self):
        self.like_num += 1
        self.save(update_fields="like_num")


class Reply(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    replyer_id = models.IntegerField(verbose_name="回复者id")
    content = models.TextField(verbose_name="回复内容")
    #根评论
    root_id = models.IntegerField(verbose_name="根评论id")
    #父回复
    fa_id = models.IntegerField(verbose_name="父评论id")
    like_num = models.IntegerField(verbose_name="点赞数",default=0)
    isLevel2 = models.IntegerField(verbose_name="是否为二级评论（一级回复）")

    def to_dic(self):
        return {
            "id":self.id,
            "create_date":self.create_date,
            "replyer_id":self.replyer_id,
            "content":self.content,
            "root_id":self.root_id,
            "fa_id":self.fa_id,
            "like_num": self.like_num,
            "isLevel2":self.isLevel2
        }




class Likes(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(verbose_name="点赞用户id")
    object_id = models.IntegerField(verbose_name="点赞对象id")
    type = models.IntegerField(verbose_name="点赞对象种类")

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
