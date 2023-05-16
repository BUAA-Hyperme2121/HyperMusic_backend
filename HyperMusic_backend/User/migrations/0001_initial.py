# Generated by Django 4.1.5 on 2023-05-16 08:16

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
                ('introduction', models.TextField(max_length=150)),
                ('cover_path', models.CharField(max_length=100)),
                ('album_num', models.IntegerField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('follow_num', models.IntegerField(default=0)),
                ('fan_num', models.IntegerField(default=0)),
                ('avatar_path', models.CharField(max_length=100)),
                ('introduction', models.TextField(max_length=150)),
                ('location', models.CharField(max_length=30)),
                ('gender', models.CharField(max_length=10)),
                ('max_record', models.IntegerField(default=20)),
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
            name='UserToLikeMusicList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0, verbose_name='用户')),
                ('music_list_id', models.IntegerField(default=0, verbose_name='喜爱歌单')),
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
