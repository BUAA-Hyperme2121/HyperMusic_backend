import random
from datetime import datetime, timedelta

from django.db.models import Count
from django.http import JsonResponse

from Music.models import MusicList, SingerToMusic, SingerToAlbum, Album, Music, Label
from User.models import Singer, UserListenHistory


# Create your views here.

# 获取某一歌单信息
def get_music_list(request):
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


# 获取某一歌手的基本信息，和他的歌曲列表, 专辑列表
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
        if not SingerToAlbum.objects.filter(singer_id=singer_id).exists():
            album_list = '该歌手尚未发布专辑'
        else:
            album_id_list = SingerToAlbum.objects.filter(singer_id=singer_id).all()
            album_list = [x.to_dic_id() for x in album_id_list]
        singer_info = Singer.objects.get(id=singer_id).to_dic()
        result = {'result': 1, 'message': '成功获取歌手基本信息', 'singer_info': singer_info, 'music_list': music_list,
                  'album_list': album_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取当前存在的歌手列表
def get_singer_list(request):
    if request.method == 'GET':
        if not Singer.objects.all().exists():
            result = {'result': 0, 'message': '当前不存在歌手'}
            return JsonResponse(result)
        singer_list_get = Singer.objects.all()
        singer_list = []
        for singer in singer_list_get:
            dic = dict()
            dic['name'] = singer.name
            dic['id'] = singer.id
            labels = [x.label_name for x in Label.objects.filter(label_singer=singer).all()]
            dic['style'] = labels
            dic['image'] = singer.cover_path
            singer_list.append(dic)
        result = {'result': 1, 'message': '获取全部歌手列表成功', 'type': 3, 'singer_list': singer_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取某一专辑信息
def get_album_info(request):
    if request.method == 'GET':
        album_id = request.POST.get('album_id')
        if not Album.objects.filter(album_id=album_id).exists():
            result = {'result': 1, 'message': '该专辑不存在'}
            return JsonResponse(result)
        album = Album.objects.get(album_id=album_id)
        album_info = album.to_dic()
        music_list = [x.to_dic() for x in album.music.all()]
        if len(music_list) == 0:
            music_list = '此专辑内尚无歌曲'
        result = {'result': 1, 'message': '成功获取专辑信息', 'album_info': album_info, 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 将一首歌曲添加到专辑/从专辑中删除
def modify_music_to_album(music_id, album_id, opration):
    if not Music.objects.filter(id=music_id).exists():
        return '歌曲不存在', False
    music = Music.objects.get(id=music_id)
    if not Album.objects.filter(id=album_id).exists():
        return '专辑不存在', False
    album = Album.objects.get(id=album_id)
    if opration == 1:
        if not album.music.objects.filter(music_id).exists():
            album.music.add(music)
            album.add_music()
            album.save()
            return '添加歌曲到专辑成功', True
        else:
            return '歌曲已经在专辑中', False
    else:
        if album.music.objects.filter(music_id).exists():
            album.music.remove(music)
            album.del_music()
            album.save()
            return '从专辑中删除歌曲成功', True
        else:
            return '歌曲不在专辑中', False


# 添加专辑
def create_album(name, publish_date, singer_name, introduction):
    if name is None or singer_name is None:
        return '专辑名字和歌手名字不能为空', False
    if Album.objects.filter(name=name).exists():
        return '已有同名专辑,请修改名字', False
    if not Singer.objects.filter(name=singer_name).exists():
        return '歌手不存在', False
    if publish_date is None:
        return '发行日期不能为空', False
    singer = Singer.objects.get(name=singer_name)
    if introduction is None:
        introduction = str(singer.name) + '的专辑'
    album = Album(name=name, publish_date=publish_date, singer=singer, introduction=introduction)
    album.save()
    return '创建专辑成功', False


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
        result = {'result': 1, 'message': '获取歌单所有类型成功', 'label_name_list': label_name_list}
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
def new_music_rank(request):
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
def surge_music_rank(request):
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
                times = music.times
                music_dic = dict()
                music_dic['id'] = get_music.id
                music_dic['name'] = get_music.music_name
                music_dic['singer_id'] = get_music.singer.id
                music_dic['singer_name'] = get_music.singer.name
                music_dic['duration'] = get_music.duration
                get_music = Music.objects.get(id=music.id)
                # 防止除0
                music_dic['times'] = get_music.listen_time / (get_music.listen_time - times + 1)
                music_times_list.append(music_dic)
        music_times_list.sort(key=lambda music: music['times'], reverse=True)
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
