from django.urls import path
from Music.views import *
urlpatterns = [
    path('get_music_list/', get_music_list),
    path('get_singer_info/', get_singer_info),
    path('get_singer_list/', get_singer_list),
    path('get_album_info/', get_album_info),
]