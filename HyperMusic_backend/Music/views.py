from django.http import JsonResponse

from Music.models import MusicList, SingerToMusic, SingerToAlbum, Album
from User.models import Singer


# Create your views here.

# 获取歌单信息
def get_music_list(request):
    if request.method == 'POST':
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


# 获取歌手的基本信息，和他的歌曲列表, 专辑列表
def get_singer_info(request):
    if request.method == 'POST':
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
            album_list = [x.to_dic() for x in album_id_list]
        singer_info = Singer.objects.get(id=singer_id).to_dic()
        result = {'result': 1, 'message': '成功获取歌手基本信息', 'singer_info': singer_info, 'music_list': music_list,
                  'album_list': album_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取歌手列表
def get_singer_list(request):
    if request.method == 'POST':
        if not Singer.objects.all().exists():
            singer_list = '当前不存在歌手'
        else:
            singer_list = [x.to_dic_id() for x in Singer.objects.all()]
        result = {'result': 1, 'message': '成功获取歌手列表', 'singer_list': singer_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取专辑信息
def get_album_info(request):
    if request.method == 'POST':
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


# 播放歌曲
def play_music(request):
    pass
