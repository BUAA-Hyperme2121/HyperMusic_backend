import time
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render
from Message.models import UserToComment, UserToComplain, MusicToComment, Comment, MusicToComplain, Complain, Message, \
    UserToMessage
from Message.models import VerifyCode
from User.models import User
from django.core.mail import send_mail
import random
#获取用户发表的评论列表
def get_user_comment_list_simple(user_id):
    return [x.id for x in UserToComment.objects.filter(user_id=user_id)]


#获取用户发表的评论列表详情
def get_user_comment_list_detail(user_id):
    return [Comment.objects.get(id=x).to_dic() for x in get_user_comment_list_simple(user_id)]


#获取用户发表的投诉列表
def get_user_complain_list_simple(user_id):
    return [x.id for x in MusicToComplain.objects.filter(user_id=user_id)]


#获取用户发表的投诉列表详情
def get_user_complain_list_detail(user_id):
    return [Complain.objects.get(id=x).to_dic() for x in get_music_complain_list_simple(user_id)]


#获取音乐的评论列表
def get_music_comment_list_simple(music_id):
    return [x.id for x in MusicToComment.objects.filter(music_id=music_id)]


#获取用户发表的评论列表详情
def get_music_comment_list_detail(music_id):
    return [Comment.objects.get(id=x).to_dic() for x in get_music_comment_list_simple(music_id)]


#获取音乐的投诉列表
def get_music_complain_list_simple(music_id):
    return [x.id for x in MusicToComplain.objects.filter(id=music_id)]


#获取音乐的投诉列表详情
def get_music_complain_list_detail(music_id):
    return [Complain.objects.get(id=x).to_dic() for x in get_music_complain_list_simple(music_id)]


def cre_complain(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.session['username']
        #检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        #从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id
        music_id = request.POST.get("music_id")
        content = request.POST.get("content")

        new_complain = Complain(user_id,music_id,content)
        new_complain.save()
        complain_id = new_complain.id
        #存储外表关系
        UserToComplain (user_id, complain_id).save()
        MusicToComplain(music_id, complain_id).save()

        return JsonResponse({'errno': 0, 'msg': "投诉成功"})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


def cre_comment(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id
        music_id = request.POST.get("music_id")
        content = request.POST.get("content")

        new_comment = Comment(user_id, music_id, content)
        new_comment.save()
        comment_id = new_comment.id
        UserToComment(user_id, comment_id).save()
        MusicToComment(music_id, comment_id).save()
        return JsonResponse({'errno': 0, 'msg': "评论成功"})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})






#获取音乐投诉列表
def list_music_complain(request):
    if request.method == 'GET':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id
        music_id = request.POST.get("music_id")

        complains = Complain.objects.filter(music_id=music_id).order_by('-create_date')
        complains = [x.to_dic() for x in complains]

        return JsonResponse({"errno": 0,
                             "msg": "获取成功成功",
                             "music_complain_list": complains})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#获取用户投诉列表
def list_user_complain(request):
    if request.method == 'GET':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]
        user_id = user.id

        complains = Complain.objects.filter(user_id=user_id).order_by('-create_date')
        complains = [x.to_dic() for x in complains]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_complain_list': complains})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#获取音乐评论列表
def list_music_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id
        music_id = request.POST.get("music_id")

        comments = Comment.objects.filter(music_id=music_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


def list_musiclist_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id
        music_id = request.POST.get("musiclist_id")

        comments = Comment.objects.filter(music_id=music_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#获取用户评论列表
def list_user_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})

        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]

        user_id = user.id

        comments = Comment.objects.filter(poster=user_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#创建一条信息
def cre_message(send_id, receiver_id, title, content):
    new_message = Message(send_id=send_id, receiver_id=receiver_id, title=title, content=content)
    new_message.save()
    UTM=UserToMessage(user_id=receiver_id, message_id=new_message.id)
    UTM.save()


#当前用户发送消息
def send_message(request):

    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})
        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]
        send_id = user.id
        receiver_id = request.POST.get('receiver_id')
        title = request.POST.get('title')
        content = request.POST.get('content')

        cre_message(send_id=send_id, receiver_id=receiver_id, title=title, content=content)

        return JsonResponse({'errno': 0,
                             'msg': "消息发送成功"})
    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})





#获取当前用户下的所有消息。
def get_user_message(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        username = request.session['username']
        # 检测用户是否登录
        if username is None:
            return JsonResponse({'errno': 1002, 'msg': "还未登录"})
        # 从数据库获取用户
        user = User.objects.filter(username=username)
        if not user.exists():
            return JsonResponse({'errno': 1003, 'msg': "用户不存在"})
        user = user[1]


        messages = Message.objects.filter(receiver_id=user.id)
        messages = [x.to_dic() for x in messages]



        return JsonResponse({'errno': 0,
                             'msg': "获取用户消息成功",
                             'messages': messages
                             })

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


def send_email_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        sms_code = '%06d' % random.randint(0, 999999)

        if send_sms_code(email, sms_code) == 1:
            return JsonResponse({'errno': 0, 'msg': "发送邮件成功"})
        else:
            return JsonResponse({'errno': 1002, 'msg': "发送邮件失败"})
        verify_code = VerifyCode(email=email, num=sms_code)
        verify_code.save()

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})



#@celery_app.task(name='send_sms_code')
def send_sms_code(to_email,sms_code):
    """
    发送邮箱验证码
    :param to_mail: 发到这个邮箱
    :return: 成功：0 失败 -1
    """
    # 生成邮箱验证码

    EMAIL_FROM = "2522820243@qq.com"  # 邮箱来自
    email_title = '邮箱激活'
    email_body = "您的邮箱注册验证码为：{0}, 该验证码有效时间为两分钟，请及时进行验证。".format(sms_code)
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [to_email])

    return send_status


def verify_code(email, sms_code):
    codes = VerifyCode.objects.filter(email=email , num=sms_code)
    if not codes.exist():
        return 0
    code = codes[0]

    code_time = code.cre_date
    interval_time = (datetime.now() - code_time).total_seconds()



    #超时
    if interval_time > 120:
        return 2
    #正常
    else:
        return 1