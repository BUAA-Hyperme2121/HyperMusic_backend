from django.http import JsonResponse
from django.shortcuts import render

from Music.models import *


# Create your views here.


def music_search(request):
    if request.method == 'GET':
        keywords = request.GET.get('keywords')
        musics= Music.objects.filter(music_name__icontains=keywords, is_audit=True).order_by('-create_date')

        musics= [ x.to_dic() for x in musics]
        return JsonResponse({  'result': 1, 'message':'搜索音乐成功', 'musics':musics    })
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})

def musiclist_search(request):
    if request.method == "GET":
        keywords = request.GET.get('keywords')
        musiclists = MusicList.objects.filter(name__icontains=keywords, is_public=True).order_by('-create_date')

        musiclists = [x.to_dic() for x in musiclists]
        return JsonResponse({'result': 1, 'message': '搜索歌单成功', 'musiclists': musiclists})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def singer_search(request):
    if request.method == "GET":
        keywords = request.GET.get('keywords')
        singers = Singer.objects.filter(name__icontains=keywords)

        singers = [x.to_dic() for x in singers]
        return JsonResponse({'result': 1, 'message': '搜索歌手成功', 'singers': singers})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def user_search(request):
    if request.method == "GET":
        keywords = request.GET.get('keywords')
        users = User.objects.filter(username__icontains=keywords).order_by('-create_date')

        users = [x.to_dic() for x in users]
        return JsonResponse({'result': 1, 'message': '搜索用户成功', 'users': users})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})