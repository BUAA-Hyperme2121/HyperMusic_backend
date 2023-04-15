from django.db import models




# Create your models here.



class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    #encoded password
    password = models.CharField(max_length=100)
    follow_num = models.IntegerField(default=0)
    fan_num = models.IntegerField(default=0)

    #个人喜爱歌单
    like_list = models.IntegerField(verbose_name="个人喜爱歌单id")

    created_time = models.DateTimeField('创建时间', auto_now_add=True)



    #增加粉丝
    def add_fan(self):
        self.fan_num += 1
        self.save(update_fields=['fan_num'])


    # 减少粉丝
    def del_fan(self):
        if self.fan_num > 0:
            self.fan_num -= 1
            self.save(update_fields=['fan_num'])


    #增加关注
    def add_follow(self):
        self.fan_num += 1
        self.save(update_fields=['follow_num'])

    # 减少关注
    def del_follow(self):
        if self.fan_num > 0:
            self.fan_num -= 1
            self.save(update_fields=['follow_num'])


#查看个人粉丝
class UserToFan(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    fan_id = models.IntegerField(verbose_name='粉丝', default=0)


# 查看个人关注
class UserToFollow(models.Model):
    user_id = models.IntegerField(verbose_name='主体', default=0)
    follow_id = models.IntegerField(verbose_name='关注的用户', default=0)


#查询个人创建歌单
class UserToMusicList(models.Model):
    user_id = models.IntegerField(verbose_name='用户',default=0)
    music_list_id = models.IntegerField(verbose_name='歌单',default=0)


#查询个人听歌历史
class UserListenHistory(models.Model):
    user_id = models.IntegerField(verbose_name='用户',default=0)
    music_id = models.IntegerField(verbose_name='音乐',default=0)
    create_date = models.DateTimeField(auto_now_add=True)


class UserToComment(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0)
    comment_id = models.IntegerField(verbose_name='评论', default=0)


class UserToComplain(models.Model):
    user_id = models.IntegerField(verbose_name='用户', default=0)
    complain_id = models.IntegerField(verbose_name='投诉', default=0)


