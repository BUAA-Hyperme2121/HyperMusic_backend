import random
from datetime import datetime, timedelta

import jwt
from django.db.models import Count
from django.http import JsonResponse

from Music.models import MusicList, SingerToMusic, Music, Label
from User.models import Singer, UserListenHistory, User


# Create your views here.

# 获取某一歌单信息
def get_music_list_info(request):
    if request.method == 'GET':
        music_list_id = request.method.get('music_list_id')
        if not MusicList.objects.filter(id=music_list_id).exists():
            result = {'result': 0, 'message': '歌单不存在'}
            return JsonResponse(result)
        get_list = MusicList.objects.get(id=music_list_id).to_dic()
        music_list_info = get_list.to_dic()
        if not get_list.music.exists():
            result = {'result': 1, 'message': '成功获取歌单', 'music_list_info': music_list_info,
                      'music_list': '此歌单尚无歌曲'}
            return JsonResponse(result)
        music_list = [x.to_dic() for x in get_list.music.all()]
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
                result = {'result': 0, 'message': "请先登录!"}
                return JsonResponse(result)
        music_id = request.GET.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        music_info = music.to_dic()
        music_info['is_like'] = False
        # 为登录用户
        if user:
            like_list = MusicList.objects.get(id=user.like_list)
            if like_list.music.objects.filter(id=music_id).exists():
                music_info['is_like'] = True
        result = {'result': 1, 'message': '获取歌曲信息成功', 'music_info': music_info}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取某一歌手的基本信息，和他的歌曲列表
def get_singer_info(request):
    if request.method == 'GET':
        singer_id = request.POST.get('singer_id')
        if not Singer.objects.filter(id=singer_id).exists():
            result = {'result': 0, 'message': '歌手不存在'}
            return JsonResponse(result)
        if not SingerToMusic.objects.filter(singer_id=singer_id).exists():
            music_list = '该歌手尚无歌曲'
        else:
            music_id_list = SingerToMusic.objects.filter(singer_id=singer_id).all()
            music_list = [x.to_dic() for x in music_id_list]
        singer_info = Singer.objects.get(id=singer_id).to_dic()
        result = {'result': 1, 'message': '成功获取歌手基本信息', 'singer_info': singer_info, 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)








