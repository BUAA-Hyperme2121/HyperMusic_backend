from django.urls import path
from User.views import *
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('change_info/', change_info),
    path('upload_music/', upload_music),
    path('del_music/', del_music),
    path('follow/', follow),
    path('unfollow', unfollow),
    path('get_follow_list', get_follow_list),
    path('get_fan_list', get_fan_list),
    path('get_create_music_list', get_create_music_list),
    path('get_like_music_list', get_like_music_list),
    path('get_like_singer_simple', get_like_singer_simple),
    path('get_recent_listen_music_list', get_recent_listen_music_list),
    path('get_most_listen_music_list', get_most_listen_music_list),
]