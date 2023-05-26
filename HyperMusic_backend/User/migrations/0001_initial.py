# Generated by Django 4.2.1 on 2023-05-24 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Singer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('introduction', models.TextField(default='暂无介绍', max_length=150)),
                ('cover_path', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('follow_num', models.IntegerField(default=0)),
                ('fan_num', models.IntegerField(default=0)),
                ('like_list', models.IntegerField(default=0, verbose_name='个人喜爱歌单id')),
                ('avatar_path', models.CharField(default='', max_length=100)),
                ('introduction', models.TextField(default='这个人很懒，什么也没有留下', max_length=150)),
                ('location', models.CharField(default='暂无', max_length=30)),
                ('gender', models.CharField(default='未知', max_length=10)),
                ('history_record', models.IntegerField(default=20)),
                ('post_num', models.IntegerField(default=0)),
                ('is_singer', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='UserListenHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_index=True, default=0, verbose_name='用户')),
                ('music_id', models.IntegerField(default=0, verbose_name='音乐')),
                ('create_date', models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserToComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='用户')),
                ('comment_id', models.IntegerField(default=0, verbose_name='评论')),
            ],
        ),
        migrations.CreateModel(
            name='UserToComplain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='用户')),
                ('complain_id', models.IntegerField(default=0, verbose_name='投诉')),
            ],
        ),
        migrations.CreateModel(
            name='UserToFan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='主体')),
                ('fan_id', models.IntegerField(default=0, verbose_name='粉丝')),
            ],
        ),
        migrations.CreateModel(
            name='UserToFollow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='主体')),
                ('follow_id', models.IntegerField(default=0, verbose_name='关注的用户')),
            ],
        ),
        migrations.CreateModel(
            name='UserToMusicList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='用户')),
                ('music_list_id', models.IntegerField(default=0, verbose_name='创建歌单')),
            ],
        ),
        migrations.CreateModel(
            name='UserToSinger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='主体')),
                ('singer_id', models.IntegerField(default=0, verbose_name='喜爱歌手')),
            ],
        ),
    ]
