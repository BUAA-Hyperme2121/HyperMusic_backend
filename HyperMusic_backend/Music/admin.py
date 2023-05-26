from django.contrib import admin
from Music.models import *
# Register your models here.
admin.site.register(Music)
admin.site.register(MusicList)
admin.site.register(SingerToMusic)
admin.site.register(Label)
