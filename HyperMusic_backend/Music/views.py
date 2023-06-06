import os
import random
import re
from ctypes import sizeof
from datetime import datetime, timedelta

import jwt
from django.db.models import Count
from django.http import JsonResponse

from Bucket import Bucket
from HyperMusic_backend.settings import MEDIA_ROOT
from Music.models import MusicList, SingerToMusic, Music, Label
from User.models import Singer, UserListenHistory, User


# Create your views here.

# 获取某一歌单信息
def get_music_list_info(request):
    if request.method == 'GET':
        music_list_id = request.GET.get('music_list_id', '')
        if len(music_list_id) == 0:
            result = {'result': 0, 'message': '请指定歌单'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=music_list_id).exists():
            result = {'result': 0, 'message': '歌单不存在'}
            return JsonResponse(result)
        get_list = MusicList.objects.get(id=music_list_id)
        music_list_info = get_list.to_dic()
        if not get_list.music.exists():
            result = {'result': 1, 'message': '成功获取歌单', 'music_list_info': music_list_info,
                      'music_list': '此歌单尚无歌曲'}
            return JsonResponse(result)
        music_list = [x.to_dic() for x in get_list.music.all()]
        # 寻找标签
        labels = Label.objects.all()
        labels_name = []
        for label in labels:
            if label.label_music_list.filter(id=music_list_id).exists():
                labels_name.append(label.label_name)
        music_list_info['labels'] = labels_name
        result = {'result': 1, 'message': '成功获取歌单', 'music_list_info': music_list_info, 'music_list': music_list}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取某一歌曲的信息
def get_music_info(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        user = None
        if JWT != "-1":
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        music_id = request.GET.get('music_id', '')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        music_info = music.to_dic()
        music_info['is_like'] = False
        # 为登录用户
        if user:
            like_list = MusicList.objects.get(id=user.like_list)
            if like_list.music.filter(id=music_id).exists():
                music_info['is_like'] = True

        # 处理歌词
        if music.lyrics_path != '':
            bucket = Bucket()
            key_name = "lyrics" + str(music_id) + '.lrc'
            download_result = bucket.download_file('hypermusic', key_name, key_name)
            if download_result == -1:
                result = {'result': 0, 'message': '歌词下载失败'}
                return JsonResponse(result)
            dir = os.path.join(MEDIA_ROOT, key_name)
            lyrics = []
            with open(dir, encoding='utf-8', mode='r') as ff:
                line = ff.readline()
                while line:
                    line = re.sub(r'\[.*]', '', line)
                    lyrics.append(line.strip())
                    line = ff.readline()

        labels = Label.objects.all()
        labels_name = []
        for label in labels:
            if label.label_music.filter(id=music_id).exists():
                labels_name.append(label.label_name)
        music_info['labels'] = labels_name
        result = {'result': 1, 'message': '获取歌曲信息成功', 'music_info': music_info}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取某一歌手的基本信息，和他的歌曲列表
def get_singer_info(request):
    if request.method == 'GET':
        singer_id = request.GET.get('singer_id', '')
        if len(singer_id) == 0:
            result = {'result': 0, 'message': '请指定歌手'}
            return JsonResponse(result)
        if not Singer.objects.filter(id=singer_id).exists():
            result = {'result': 0, 'message': '歌手不存在'}
            return JsonResponse(result)
        if not SingerToMusic.objects.filter(singer_id=singer_id).exists():
            music_list = '该歌手尚无歌曲'
        else:
            music_id_list = [x.music_id for x in SingerToMusic.objects.filter(singer_id=singer_id).all()]
            music_list = [Music.objects.get(id=x).to_dic() for x in music_id_list]
        singer_info = Singer.objects.get(id=singer_id).to_dic()
        result = {'result': 1, 'message': '成功获取歌手基本信息', 'singer_info': singer_info, 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


def change_favorites_info(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        favorites_id = request.POST.get('favorites_id', '')
        if favorites_id == '':
            result = {'result': 0, 'message': '请指定要修改的收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=favorites_id, creator=user).exists():
            result = {'result': 0, 'message': '此收藏夹不存在或权限不足'}
            return JsonResponse(result)
        favorites = MusicList.objects.get(id=favorites_id, creator=user)
        name = request.POST.get('name', '')
        # 修改名字
        if name != '':
            favorites.name = name
        description = request.POST.get('description', '')
        # 修改简介
        if description != '':
            favorites.description = description
        music_list_cover = request.POST.get('cover', None)
        # 修改封面
        if music_list_cover:
            bucket = Bucket()
            if music_list_cover:
                if music_list_cover.size > 2 * 1024 * 1024:
                    result = {'result': 0, 'message': '封面大小不能超过2M'}
                    return JsonResponse(result)

                suffix_music_list_cover = '.' + music_list_cover.name.split('.')[-1]
                # 修改封面文件流对象的名称
                music_list_cover.name = 'music_list_cover' + str(favorites.id) + suffix_music_list_cover

                # 临时保存到本地
                music_list_cover_dir = os.path.join(MEDIA_ROOT, music_list_cover.name)

                with open(music_list_cover_dir, 'wb+') as destination:
                    for chunk in music_list_cover.chunks():
                        destination.write(chunk)
                    destination.close()

                # 上传封面
                upload_result = bucket.upload_file('hypermusic', music_list_cover.name, music_list_cover.name)

                if upload_result == -1:
                    result = {'result': 0, 'message': '上传失败'}
                    # 删除本地存储
                    os.remove(music_list_cover_dir)
                    return JsonResponse(result)
                # 获取审核结果
                audit_dic = bucket.image_audit('hypermusic', music_list_cover.name)

                if audit_dic.get('result') != 0:
                    bucket.delete_object('hypermusic', music_list_cover.name)
                    os.remove(music_list_cover_dir)
                    result = {'result': 0, 'message': '歌单封面审核失败'}
                    return JsonResponse(result)

                # 获取存储路径
                cover_path = bucket.query_object('hypermusic', music_list_cover.name)
                if not cover_path:
                    os.remove(music_list_cover_dir)
                    result = {'result': 0, 'message': '上传封面失败'}
                    return JsonResponse(result)
                favorites.cover_path = cover_path
                # 删除本地文件
                os.remove(music_list_cover_dir)
        favorites.save()
        result = {'result': 1, 'message': '修改收藏夹信息成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)