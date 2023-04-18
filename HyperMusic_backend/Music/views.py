from django.shortcuts import render
from User.models import UserToFollow
# Create your views here.


#得到用户的关注列表
def get_follow_list_simple(user_id):
    return [x.id for x in UserToFollow.objects.filter(id=user_id)]

def get_follow_list_detail(user_id):
    return [User.objects.get(id=x).to_dic() for x in get_follow_list_simple(user_id)]