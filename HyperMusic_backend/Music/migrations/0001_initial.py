# Generated by Django 4.1.5 on 2023-05-16 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('file_loc', models.CharField(max_length=100)),
                ('likes', models.IntegerField(default=0)),
                ('listen_time', models.IntegerField(default=0)),
                ('music_front', models.ImageField(upload_to='')),
                ('front_path', models.CharField(max_length=100)),
                ('music_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('duration', models.CharField(max_length=25)),
                ('words', models.TextField(max_length=1000)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Music_Uploader', to='User.user')),
                ('singer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Music_Creator', to='User.singer')),
            ],
        ),
        migrations.CreateModel(
            name='SingerToAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singer_id', models.IntegerField(default=0, verbose_name='歌手')),
                ('album_id', models.IntegerField(default=0, verbose_name='专辑')),
            ],
        ),
        migrations.CreateModel(
            name='SingerToMusic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singer_id', models.IntegerField(default=0, verbose_name='歌手')),
                ('music_id', models.IntegerField(default=0, verbose_name='歌曲')),
            ],
        ),
        migrations.CreateModel(
            name='MusicList',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('music_num', models.IntegerField(default=0)),
                ('music_list_front', models.ImageField(upload_to='')),
                ('front_path', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=200)),
                ('listen_time', models.IntegerField(default=0)),
                ('type', models.IntegerField()),
                ('is_share', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='MusicList_Creator', to='User.user')),
                ('music', models.ManyToManyField(to='Music.music')),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label_name', models.CharField(max_length=100)),
                ('label_music', models.ManyToManyField(to='Music.music')),
                ('label_music_list', models.ManyToManyField(to='Music.musiclist')),
                ('label_singer', models.ManyToManyField(to='User.singer')),
            ],
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('music_num', models.IntegerField(default=0)),
                ('cover_path', models.CharField(max_length=100)),
                ('cover', models.ImageField(upload_to='')),
                ('publish_date', models.DateField()),
                ('introduction', models.TextField(max_length=200)),
                ('music', models.ManyToManyField(to='Music.music')),
                ('singer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Singer', to='User.singer')),
            ],
        ),
    ]
