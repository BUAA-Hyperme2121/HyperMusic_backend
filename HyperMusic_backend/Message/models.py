from django.db import models
from Music.models import Music, MusicList
from User.models import User, Singer


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
            "poster_avatar_path":User.objects.get(id=self.poster_id).avatar_path,
            "poster_name":User.objects.get(id=self.poster_id).username,
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
    audit_time = models.DateTimeField(blank=True, null=True)
    #result: 1 -成功 2 -失败
    result = models.IntegerField(verbose_name="审核结果", blank=True, null=True)
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
            "poster_name": User.objects.get(id=self.poster_id).username,
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
            "poster_name": User.objects.get(id=self.poster_id).username,
        }

#消息
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
    # 1 评论 2 点赞 3 关注 4 投诉 5 系统消息  6-回复 7-喜爱
    message_type = models.IntegerField(verbose_name="消息种类")
    #0 - 未读 1 - 已读
    state = models.IntegerField(verbose_name="读状态", default=0)
    from_object_id = models.IntegerField(verbose_name="来源id", default=0)


    def __str__(self):
        return '站内信' + self.title


    def to_dic(self):
        like_info={}
        if self.message_type == 2:
            if type == 1:
                like_info = Music.objects.get(id=self.object_id).to_dic()
            elif type == 2:
                like_info = MusicList.objects.get(id=self.object_id).to_dic()
            elif type == 3:
                like_info = Post.objects.get(id=self.object_id).to_dic()


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
            "poster_name":User.objects.get(id=self.poster_id).username,
            "poster_avatar_path":User.objects.get(id=self.poster_id).avatar_path,
            "like_info":like_info,
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
        if self.type == 1:
            object= Music.objects.get(id=self.object_id)
            object_name=object.music_name
            object_cover_path = object.cover_path
            object_owner_id = object.singer.id
            object_owner_name = Singer.objects.get(id=object_owner_id).name
        elif self.type == 2:
            object = MusicList.objects.get(id=self.object_id)
            object_name = object.name
            object_cover_path = object.cover_path
            object_owner_id = object.creator.id
            object_owner_name = User.objects.get(id=object_owner_id).username
        return {
            "id":self.id,
            "poster_id":self.poster_id,
            "content":self.content,
            "create_date":self.create_date,
            "like_num":self.like_num,
            "comment_num":self.comment_num,
            "type":self.type,
            "object_id":self.object_id,
            "poster_avatar_path":User.objects.get(id = self.poster_id).avatar_path,
            "poster_name":User.objects.get(id = self.poster_id).username,
            "object_name": object_name,
            "object_cover_path": object_cover_path,
            "object_owner_name": object_owner_name,
        }


    def add_like(self):
        self.like_num += 1
        self.save(update_fields="like_num")


class JobToMusic(models.Model):
    job_id = models.CharField(verbose_name='审核任务id', max_length=114, default='')
    music_id = models.IntegerField(verbose_name='音乐id', default=0)


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
        if self.isLevel2:
            fa_poster_id = Comment.objects.get(id=self.root_id).poster_id
            fa_content = Comment.objects.get(id=self.root_id).content

        else:
            fa_poster_id = Reply.objects.get(id=self.fa_id).replyer_id
            fa_content = Reply.objects.get(id=self.fa_id).content

        return {
            "id":self.id,
            "create_date":self.create_date,
            "replyer_id":self.replyer_id,
            "content":self.content,
            "root_id":self.root_id,
            "fa_id":self.fa_id,
            "like_num": self.like_num,
            "isLevel2":self.isLevel2,
            "poster_name":User.objects.get(id=self.replyer_id).username,
            "poster_avatar":User.objects.get(id=self.replyer_id).avatar_path,
            "fa_poster_name":User.objects.get(id=fa_poster_id).username,
            "fa_content": fa_content,
        }




class Likes(models.Model):

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
