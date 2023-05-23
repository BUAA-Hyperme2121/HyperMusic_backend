from django.urls import path,include
from Message.views import *
urlpatterns = [
    path('cre_complain/', cre_complain),
    path('cre_comment/', cre_comment),
    path('list_complain/', list_complain ),
    #path('list_user_complain/', list_user_complain ),
    path('list_object_comment/', list_object_comment),
    path('list_user_comment/', list_user_comment),
    path('send_message/', send_message),
    path('send_email_register/', send_email_register),
    path('get_user_message/', get_user_message),
    path('del_o')
]