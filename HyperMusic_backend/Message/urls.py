from django.urls import path,include
from views import *
urlpatterns = [
    path('cre_complain/', cre_complain),
    path('cre_comment/', cre_comment),
    path('list_music_complain/',list_music_complain ),
    path('list_user_complain/',list_user_complain ),
    path('list_music_comment/',list_music_comment),
    path('list_user_comment/',list_user_comment),

]