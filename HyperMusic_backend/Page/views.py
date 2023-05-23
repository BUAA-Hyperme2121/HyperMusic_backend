from datetime import timedelta, datetime
import random

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from Music.models import MusicList, Label, Music
from User.models import User, UserListenHistory


# Create your views here.

# 获取用户信息
def get_user_info(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id', None)
        if user_id is None:
            result = {'result': 0, 'message': '用户id不能为空'}
            return JsonResponse(result)
        if not User.objects.filter(id=user_id).exists():
            result = {'result': 0, 'message': '用户不存在'}
            return JsonResponse(result)
        user = User.objects.get(id=user_id)
        result = {'result': 1, 'message': '成功获取用户信息', 'user_info': user.to_dic()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取全部歌单列表
def get_all_music_list(request):
    if request.method == 'GET':
        music_list_get = MusicList.objects.all()
        music_list = []
        for ml in music_list_get:
            dic = dict()
            dic['name'] = ml.name
            dic['id'] = ml.id
            labels = [x.label_name for x in Label.objects.filter(label_music_list=ml).all()]
            dic['style'] = labels
            dic['image'] = ml.front_path
            music_list.append(dic)
        result = {'result': 1, 'message': '获取全部歌单成功', 'type': 2, 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


def generate_music_dic(get_music_list):
    return_music_list = []
    for music in get_music_list:
        dic = dict()
        dic['id'] = music.id
        dic['name'] = music.music_name
        dic['singer_name'] = music.singer.name
        dic['singer_id'] = music.singer.id
        dic['duration'] = music.duration
        return_music_list.append(dic)
    return return_music_list


# 获取热歌榜50首歌
def get_hot_rank(request):
    if request.method == 'GET':
        # 最近两周周内播放量最高的50首歌
        monday = datetime.today()
        one_day = timedelta(days=-1)
        while monday.weekday() != 0:
            monday += one_day
        one_week = timedelta(days=-7)
        last_monday = monday + one_week
        hot_list = UserListenHistory.objects.filter(create_date__gte=last_monday). \
                       values('music_id').annotate(times=Count('music_id')).order_by('-times')[:10]
        hot_music_list = generate_music_dic(hot_list)
        result = {'result': 1, 'message': '获取热歌榜成功', 'hot_music_list': hot_music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取新歌榜50首歌
def get_new_music_rank(request):
    if request.method == 'GET':
        monday = datetime.today()
        one_day = timedelta(days=-1)
        while monday.weekday() != 0:
            monday += one_day
        one_week = timedelta(days=-7)
        last_monday = monday + one_week
        # 最近两周内新发布的，播放量最多的50首歌
        new_list = Music.objects.filter(create_time__gte=last_monday).all().order_by('-listen_time')[:50]
        new_music_list = generate_music_dic(new_list)
        result = {'result': 1, 'message': '获取新歌榜成功', 'new_music_list': new_music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取飙升榜50首歌
def get_surge_music_rank(request):
    if request.method == 'GET':
        monday = datetime.today()
        one_day = timedelta(days=-1)
        while monday.weekday() != 0:
            monday += one_day
        one_week = timedelta(days=-14)
        last_monday = monday + one_week
        # 获取最近两周内的每首歌的播放量
        times_record = UserListenHistory.objects.filter(create_date__gte=last_monday). \
            values('music_id').annotate(times=Count('music_id')).order_by('-times')
        music_times_list = []
        for music in times_record:
            # 不计算新歌
            if Music.objects.filter(id=music.id).exists():
                get_music = Music.objects.get(id=music.id)
                times = music.times
                music_dic = dict()
                music_dic['id'] = get_music.id
                music_dic['name'] = get_music.music_name
                music_dic['singer_id'] = get_music.singer.id
                music_dic['singer_name'] = get_music.singer.name
                music_dic['duration'] = get_music.duration
                # 防止除0
                music_dic['times'] = get_music.listen_time / (get_music.listen_time - times + 1)
                music_times_list.append(music_dic)
        music_times_list.sort(key=lambda music_: music_['times'], reverse=True)
        surge_music_list = music_times_list[:50]
        result = {'result': 1, 'message': '成功获取飙升榜', 'surge_music_list': surge_music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取原创榜内容
def original_music_rank(request):
    if request.method == 'GET':
        pass
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取推荐歌单列表
def get_recommend_music_list(request):
    if request.method == 'GET':
        # 获取随机十首歌作为推荐歌曲
        cnt = 0
        recommend_list = []
        # 不足十首歌,返回错误
        if Music.objects.all().count() < 10:
            result = {'result': 0, 'message': '歌曲库不足十首歌'}
            return JsonResponse(result)
        while True:
            if cnt == 10:
                break
            music_all = Music.objects.all()
            for music in music_all:
                r = random.randint(0, 100)
                if r < 10:
                    dic = dict()
                    dic['name'] = music.music_name
                    dic['id'] = music.id
                    labels = [x.label_name for x in Label.objects.filter(label_music=music).all()]
                    dic['style'] = labels
                    dic['image'] = music.front_path
                    recommend_list.append(dic)
                    cnt += 1
        result = {'result': 1, 'message': '获取推荐歌单成功', 'type': 1, 'recommend_list': recommend_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取歌单所有类型
def get_music_list_style(request):
    if request.method == 'GET':
        if not Label.objects.all().exists():
            result = {'result': 0, 'message': '目前尚不存在标签'}
            return JsonResponse(result)
        labels = Label.objects.all()
        label_name_list = []
        for label in labels:
            if label.label_music_list.objects.first().exists():
                label_name_list.append(label.label_name)
        result = {'result': 1, 'message': '获取歌单所有类型成功', 'label_name_list': label_name_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取歌手所有类型
def get_singer_style(request):
    if request.method == 'GET':
        if not Label.objects.all().exists():
            result = {'result': 0, 'message': '目前尚不存在标签'}
            return JsonResponse(result)
        labels = Label.objects.all()
        label_name_list = []
        for label in labels:
            if label.label_singer.objects.first().exists():
                label_name_list.append(label.label_name)
        result = {'result': 1, 'message': '获取歌手所有类型成功', 'label_name_list': label_name_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)
