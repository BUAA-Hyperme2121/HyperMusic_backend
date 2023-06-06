from django.db import models


# Create your models here.


# 歌手
class Singer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    introduction = models.TextField(max_length=150, default='暂无介绍')
    cover_path = models.CharField(max_length=100, default='https://hypermusic-1317300880.cos.ap-beijing.myqcloud.com/Default_Singer_Avator.png')

    def to_dic(self):
        return {
            'id': self.id,
            'name': self.name,
            'cover_path': self.cover_path,
            'introduction': self.introduction
        }


class User(models.Model):
    # 基本信息
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)  # 头像,个人简介,所在地, 性别

    # 维护信息
    follow_num = models.IntegerField(default=0)
    fan_num = models.IntegerField(default=0)
    like_list = models.IntegerField(verbose_name="个人喜爱歌单id", default=0)

    # 头像路径
    avatar_path = models.CharField(max_length=100, default='https://hypermusic-1317300880.cos.ap-beijing.myqcloud.com/Default_User_Avator.png')

    # 可选信息: 简介,所在地,性别
    introduction = models.TextField(max_length=150, default='这个人很懒，什么也没有留下')
    location = models.CharField(max_length=30, default='暂无')
    gender = models.CharField(max_length=10, default='未知')

    # 个性设置: 最近播放记录数量
    history_record = models.IntegerField(default=20)

    # 动态数量
    post_num = models.IntegerField(default=0)

    # 判断信息: 歌手认证, 管理员认证
    is_singer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def to_dic(self):
        return {
            'id': self.id,
            'username': self.username,
            'introduction': self.introduction if self.introduction is not None else '暂无',
            'location': self.location if self.location is not None else '暂无',
            'gender': self.gender,
            'avatar_path': self.avatar_path,
            'follow_num': self.follow_num,
            'fan_num': self.fan_num,
            'post_num': self.post_num,
            'history_record': self.history_record,
            'is_singer': self.is_singer,
            'is_admin': self.is_admin
        }

    # 增加粉丝
    def add_fan(self):
        self.fan_num += 1
        self.save(update_fields=['fan_num'])

    # 减少粉丝
    def del_fan(self):
        if self.fan_num > 0:
            self.fan_num -= 1
            self.save(update_fields=['fan_num'])

    # 增加关注
    def add_follow(self):
        self.follow_num += 1
        self.save(update_fields=['follow_num'])

    # 减少关注
    def del_follow(self):
        if self.fan_num > 0:
            self.follow_num -= 1
            self.save(update_fields=['follow_num'])


# 个人粉丝
class UserToFan(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    fan_id = models.IntegerField(verbose_name='粉丝', default=0)


# 个人关注
class UserToFollow(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    follow_id = models.IntegerField(verbose_name='关注的用户', default=0)


# 个人喜欢歌手
class UserToSinger(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    singer_id = models.IntegerField(verbose_name='喜爱歌手', default=0)


# 个人创建歌单
class UserToMusicList(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0)
    music_list_id = models.IntegerField(verbose_name='创建歌单', default=0)


# 查询个人听歌历史
class UserListenHistory(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0, db_index=True)
    music_id = models.IntegerField(verbose_name='音乐', default=0)
    create_date = models.DateTimeField(auto_now_add=True, db_index=True)


class UserToComment(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)


class UserToComplain(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0)
    complain_id = models.IntegerField(verbose_name='投诉', default=0)
