from django.urls import path
from Music.views import *
urlpatterns = [
    path('get_music_list/', get_music_list_info),
    path('get_singer_info/', get_singer_info),
    path('get_music_list_info/', get_music_list_info),
    path('get_music_info/', get_music_info),

]