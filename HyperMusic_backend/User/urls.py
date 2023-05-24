from django.urls import path
from views import *
urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('change_info/', change_info),
    path('upload_music/', upload_music),
    path('del_music/', del_music),
    path('follow/', follow),
    path('unfollow/', unfollow),
    path('get_follow_list/', get_follow_list),
    path('get_fan_list/', get_fan_list),
    path('get_create_music_list/', get_create_music_list),
    path('get_like_singer_simple/', get_like_singer_simple),
    path('get_recent_listen_music_list/', get_recent_listen_music_list),
    path('get_most_listen_music_list/', get_most_listen_music_list),
    path('like_music/', like_music),
    path('unlike_music/', unlike_music),
    path('mark_music/', mark_music),
    path('unlike_music/', unmark_music),
    path('cerate_favorites/', create_favorites),
    path('get_favorites/', get_favorites),
    path('share_favorites/', share_favorites),
    path('unshare_favorites/', unshare_favorites),
    path('mark_music_list/', mark_music_list),
    path('set_history_record/', set_history_record),
]