import random
from datetime import timedelta, datetime

import jwt
from django.db.models import Count
from django.http import JsonResponse

from Music.models import MusicList, Label, Music
from User.models import User, UserListenHistory, Singer, UserToFollow


# Create your views here.

# 获取用户信息
def get_user_info(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT')
        user = None
        if JWT != "-1":
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        get_user_id = request.GET.get('user_id', None)
        if get_user_id is None:
            result = {'result': 0, 'message': '用户id不能为空'}
            return JsonResponse(result)
        if not User.objects.filter(id=get_user_id).exists():
            result = {'result': 0, 'message': '用户不存在'}
            return JsonResponse(result)
        get_user = User.objects.get(id=get_user_id)
        dic = get_user.to_dic()
        dic['is_follow'] = False
        # 当前用户为登录用户
        if user:
            # 判断此用户登录用户是否关注过
            if UserToFollow.objects.filter(user_id=user.id, follow_id=get_user_id).exists():
                dic['is_follow'] = True
        result = {'result': 1, 'message': '成功获取用户信息', 'user_info': dic}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 获取全部歌单列表
def get_all_music_list(request):
    if request.method == 'GET':
        # 获取公开的收藏夹
        music_list_get = MusicList.objects.filter(type=1, is_public=True).all()[:200]
        music_list_all = []
        for ml in music_list_get:
            dic = dict()
            dic['name'] = ml.name
            dic['id'] = ml.id
            dic['creator_id'] = ml.creator.id
            label_list = Label.objects.all()
            labels = list()
            for label in label_list:
                if label.label_music_list.filter(id=ml.id):
                    labels.append(label.label_name)
            dic['labels'] = labels
            dic['cover_path'] = ml.cover_path
            music_list_all.append(dic)
        result = {'result': 1, 'message': '获取全部歌单成功', 'type': 2, 'music_list_all': music_list_all}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取全部歌手列表
def get_all_singer(request):
    if request.method == 'GET':
        singers = Singer.objects.all()[:200]
        singer_list = []
        for singer in singers:
            dic = dict()
            dic['id'] = singer.id
            dic['name'] = singer.name
            label_list = Label.objects.all()
            labels = list()
            for label in label_list:
                if label.label_singer.filter(id=singer.id):
                    labels.append(label.label_name)
            dic['labels'] = labels
            dic['cover_path'] = singer.cover_path
            singer_list.append(dic)
        result = {'result': 1, 'message': '获取全部列表成功', 'type': 3, 'singer_list': singer_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


# 获取全部歌曲
def get_all_music(request):
    if request.method == 'GET':
        music_all = Music.objects.all()[:200]
        music_list = []
        for music in music_all:
            dic = dict()
            dic['name'] = music.music_name
            dic['id'] = music.id
            label_list = Label.objects.all()
            labels = list()
            for label in label_list:
                if label.label_music.filter(id=music.id):
                    labels.append(label.label_name)
            dic['labels'] = labels
            dic['cover_path'] = music.cover_path
            music_list.append(dic)
        result = {'result': 1, 'message': '获取全部歌曲成功', 'type': 1, 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误!'}
        return JsonResponse(result)


def generate_music_dic(music):
    dic = dict()
    dic['id'] = music.id
    dic['music_name'] = music.music_name
    dic['singer_name'] = music.singer.name
    dic['singer_id'] = music.singer.id
    dic['cover_path'] = music.cover_path
    dic['music_path'] = music.music_path
    return dic


# 获取热歌榜50首歌
def get_hot_music_rank(request):
    if request.method == 'GET':
        # 最近两周周内播放量最高的50首歌
        monday = datetime.today()
        one_day = timedelta(days=-1)
        while monday.weekday() != 0:
            monday += one_day
        one_week = timedelta(days=-7)
        last_monday = monday + one_week
        # 获取最近两周内歌曲播放量,降序排列
        history_record = UserListenHistory.objects.filter(create_date__gte=last_monday). \
                             values('music_id').annotate(times=Count('music_id')).order_by('-times')[:10]
        hot_music_rank = []
        for history in history_record:
            music = Music.objects.get(id=history['music_id'])
            hot_music_rank.append(generate_music_dic(music))
        result = {'result': 1, 'message': '获取热歌榜成功', 'hot_music_rank': hot_music_rank}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
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
        new_music_list = Music.objects.filter(create_date__gte=last_monday).all().order_by('-listen_nums')[:50]
        new_music_rank = []
        for music in new_music_list:
            new_music_rank.append(generate_music_dic(music))
        result = {'result': 1, 'message': '获取新歌榜成功', 'new_music_rank': new_music_rank}
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
            # 不计算两周前才发布的新歌
            if Music.objects.filter(id=music['music_id'], create_date__gte=last_monday).exists():
                get_music = Music.objects.get(id=music['music_id'], create_date__gte=last_monday)
                times = music['times']
                dic = generate_music_dic(get_music)
                # 防止除0
                dic['times'] = get_music.listen_nums / (get_music.listen_nums - times + 1)
                music_times_list.append(dic)
        # 根据播放次数升高比例降序排列
        music_times_list.sort(key=lambda music_: music_['times'], reverse=True)
        surge_music_rank = music_times_list[:50]
        result = {'result': 1, 'message': '成功获取飙升榜', 'surge_music_rank': surge_music_rank}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取原创榜内容
def get_original_music_rank(request):
    if request.method == 'GET':
        # 获取原创歌曲
        original_music_list = Music.objects.filter(is_original=True).all().order_by('-listen_nums')[:50]
        original_music_rank = []
        for music in original_music_list:
            original_music_rank.append(generate_music_dic(music))
        result = {'result': 1, 'message': '成功获取原创榜', 'original_music_rank': original_music_rank}
        return JsonResponse(result)
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
                    dic['music_name'] = music.music_name
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
