from django.urls import path
from views import *
urlpatterns = [
    path('get_user_info/', get_user_info),
    path('get_all_music_list/', get_all_music_list),
    path('get_hot_rank/', get_hot_rank),
    path('get_new_music_rank/', get_new_music_rank),
    path('get_surge_music_rank/', get_surge_music_rank),
    path('get_recommend_music_list/', get_recommend_music_list),
    path('get_music_list_style/', get_music_list_style),
    path('get_singer_style/', get_singer_style),
]