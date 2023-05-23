from django.contrib import admin
from django.urls import path, include
from Index.views import *
urlpatterns = [
    path('singer_search/', singer_search),
    path('user_search/', user_search),
    path('musiclist_search/', musiclist_search),
    path('music_search/', music_search),
]