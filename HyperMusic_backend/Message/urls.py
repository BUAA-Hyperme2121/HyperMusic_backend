from django.urls import path,include
from Message.views import *
urlpatterns = [
    path('cre_complain/', cre_complain),
    path('cre_comment/', cre_comment),
    path('list_complain/', list_complain ),
    path('list_user_complain/', list_user_complain ),
    path('list_object_comment/', list_object_comment),
    path('list_user_comment/', list_user_comment),
    path('send_message/', send_message),
    path('send_email_register/', send_email_register),
    path('get_user_message/', get_user_message),
    path('get_reply/', get_reply),
    path('del_comment/', del_comment),
    path('del_post/', del_post),
    path('del_object/', del_object),
    path('audit/', audit),
    path('get_complain_detail/', get_complain_detail),
    path('like/',like),
    path('cre_post/',cre_post),
    path('cre_reply/',cre_reply),
    path('get_follow_post/', get_follow_post),
    path('get_user_post/', get_user_post),
    path('get_complain_detail/', get_complain_detail),
    path('cancel_like/', cancel_like),
    path('ai_audit/', ai_audit),
    path('modify_comment/', modify_comment),
]