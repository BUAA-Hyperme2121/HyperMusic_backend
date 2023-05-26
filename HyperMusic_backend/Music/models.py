from django.db import models
from User.models import User, Singer


# Create your models here.


# 歌曲
class Music(models.Model):
    # 基本信息
    id = models.AutoField(primary_key=True)
    music_name = models.CharField(max_length=100)
    create_date = models.DateTimeField('创建时间', auto_now_add=True)
    # 上传者和歌手
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Music_Uploader')
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='Music_Singer')
    # 音源路径,歌词路径,封面路径
    music_path = models.CharField(max_length=100, default='')
    cover_path = models.CharField(max_length=100, default='')
    lyrics_path = models.CharField(max_length=100, default='')
    # 维护信息: 喜欢数,播放量,是否原创
    likes = models.IntegerField(default=0)
    listen_nums = models.IntegerField(default=0)
    is_original = models.BooleanField(default=False)
    # 可选信息: 歌曲描述
    description = models.TextField(default='这首歌还没有介绍哦')
    is_audit = models.BooleanField(default=False)

    def to_dic(self):
        return {
            'id': self.id,
            'music_name': self.music_name,
            'singer_id': self.singer.id,
            'singer_name': self.singer.name,
            'music_path': self.music_path,
            'cover_path': self.cover_path,
            'lyrics_path': self.lyrics_path,
            'listen_nums': self.listen_nums,
            'description': self.description,
        }

    def add_listen_times(self):
        self.listen_nums += 1
        self.save(update_fields=['listen_nums'])

    def add_likes(self):
        self.likes += 1
        self.save(update_fields=['likes'])

    def del_likes(self):
        self.likes -= 1
        self.save(update_fields=['likes'])


# 用户创建的收藏夹/分享的歌单
class MusicList(models.Model):
    # 基本信息
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    create_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='MusicList_Creator')

    # 收录歌曲
    music = models.ManyToManyField(to=Music)

    # 维护信息: 歌曲数量,歌单类型,是否分享
    music_num = models.IntegerField(default=0)
    # 歌单类型type: 1 收藏夹 2 喜欢歌单
    type = models.IntegerField(default=1)
    # 是否公开分享，默认不分开
    is_public = models.BooleanField(default=False)

    # 封面路径
    cover_path = models.CharField(max_length=100, default='')
    # 可选信息: 歌单简介
    description = models.TextField(max_length=200, default='此歌单还没有介绍哦')

    def to_dic(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator.id,
            'creator_name': self.creator.username,
            'cover_path': self.cover_path,
            'music_num': self.music_num,
            'is_public': self.is_public,
            'type': self.type
        }

    def change_cover(self, new_path):
        self.front_path = new_path
        self.save(update_fields=['new_path'])

    def add_music(self):
        self.music_num += 1
        self.save(update_fields=['music_num'])

    def del_music(self):
        self.music_num -= 1
        self.save(update_fields=['music_num'])


# 歌曲标签
class Label(models.Model):
    id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=100)
    label_music = models.ManyToManyField(to=Music)
    label_music_list = models.ManyToManyField(to=MusicList)
    label_singer = models.ManyToManyField(to=Singer)


# 歌手的歌曲
class SingerToMusic(models.Model):
    singer_id = models.IntegerField(verbose_name='歌手', default=0)
    music_id = models.IntegerField(verbose_name='歌曲', default=0)
