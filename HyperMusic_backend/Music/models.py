from django.db import models
from User.models import User, Singer


# Create your models here.


# 歌曲
class Music(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Music_Uploader')
    file_loc = models.CharField(max_length=100)
    likes = models.IntegerField()
    listen_times = models.IntegerField()
    # music_comments = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='Comment')
    # music_complains = models.ForeignKey(Complain, on_delete=models.CASCADE, related_name='Complain')
    music_cover_path = models.CharField()
    music_name = models.CharField(max_length=100)
    description = models.TextField()
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='Music_Creator')
    duration = models.CharField(max_length=25)
    # 歌词
    words = models.TextField(max_length=1000)

    def to_dic(self):
        return {
            'music_id': self.id,
            'music_name': self.music_name,
            'duration': self.duration,
            'singer_id': self.singer.id,
            'singer_name': self.singer.name,
            'creator': self.creator,
            'music_cover_path': self.music_cover_path,
            'likes': self.likes,
            'listen_times': self.listen_times
        }

    def get_words(self):
        return self.words

    def add_listen_times(self):
        self.listen_times += 1
        self.save(update_fields="listen_times")

    def add_likes(self):
        self.likes += 1
        self.save(update_fields='likes')

    def del_likes(self):
        self.likes -= 1
        self.save(update_fields='likes')


# 歌手专辑
class Album(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    music = models.ManyToManyField(to=Music)
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='Singer')
    music_num = models.IntegerField(default=0)
    cover_path = models.CharField()
    publish_date = models.DateField()
    description = models.TextField(max_length=200)

    def to_dic_id(self):
        return {
            'id': self.id,
            'name': self.name,
            'cover_path': self.cover_path,
            'music_num': self.music_num
        }

    def to_dic(self):
        return {
            'name': self.name,
            'cover_path': self.cover_path,
            'publish_date': self.publish_date,
            'description': self.description
        }


# 用户创建的歌单/收藏夹
class MusicList(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    create_date = models.DateTimeField(auto_now_add=True)
    music_list_profile = models.TextField()
    music = models.ManyToManyField(to=Music)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='MusicList_Creator')
    views = models.IntegerField()
    music_num = models.IntegerField(default=0)
    cover_path = models.CharField()

    def to_dic_id(self):
        return {
            "name": self.name,
            "id": self.id,
            "cover_path": self.cover_path,
            "music_num": self.music_num
        }

    def to_dic(self):
        return {
            "name": self.name,
            "cover_path": self.cover_path,
            "song_count": self.music_num
        }

    def change_cover(self, new_path):
        self.cover_path = new_path
        self.save(update_fields='cover_path')

    def add_music_num(self):
        self.music_num += 1
        self.save(update_fields='music_num')

    def del_music_num(self):
        self.music_num -= 1
        self.save(update_fields='music_num')


# 歌曲标签
class Label(models.Model):
    id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=100)
    label_music = models.ManyToManyField(to=Music)
    label_music_list = models.ManyToManyField(to=MusicList)


# 歌手的歌曲
class SingerToMusic(models.Model):
    singer_id = models.IntegerField(verbose_name='歌手', default=0)
    music_id = models.IntegerField(verbose_name='歌曲', default=0)


# 歌手的专辑
class SingerToAlbum(models.Model):
    singer_id = models.IntegerField(verbose_name='歌手', default=0)
    album_id = models.IntegerField(verbose_name='专辑', default=0)
