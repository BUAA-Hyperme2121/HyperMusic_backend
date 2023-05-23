import random
from datetime import datetime

import jwt
from django.core.mail import send_mail
from django.http import JsonResponse
from Music.models import *
from Message.models import *
from User.models import User
from django.utils import timezone

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


#投诉种类 1 为歌曲 2为歌单
def cre_complain(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        # 从数据库获取用户
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)



        user_id = user.id
        object_id = request.POST.get("object_id")
        content = request.POST.get("content")
        type = request.POST.get("type")
        title = request.POST.get("title")


        new_complain = Complain(poster_id=user_id, object_id=object_id, content=content, type=type, state=1)
        new_complain.save()
        complain_id = new_complain.id
        #存储外表关系

        UserToComplain(user_id, complain_id).save()

        # 投诉类型为音乐
        print(type)

        if type == '1':
            music=Music.objects.filter(id=object_id)

            if not music.exists():
                return JsonResponse({'result': 0, 'msg': "音乐不存在"})
            MusicToComplain(music_id=object_id, complain_id=complain_id).save()
        # 投诉类型为歌单

        elif type == '2':

            musiclist = MusicList.objects.filter(id=object_id)
            print(musiclist)
            if not musiclist.exists():
                return JsonResponse({'result': 0, 'msg': "歌单不存在"})
            MusicListToComplain(musiclist_id=object_id, complain_id=complain_id).save()

        return JsonResponse({
                            'result': 0,
                            'msg': "投诉成功",
                            'state':new_complain.state,
                             })

    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


#0 是音乐 1 是歌单 2 是动态
def cre_comment(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）

        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        user_id = user.id
        object_id = request.POST.get("object_id")
        content = request.POST.get("content")
        type = request.POST.get("type")

        new_comment = Comment(poster_id=user_id, object_id=object_id, content=content, type=type)
        new_comment.save()
        comment_id = new_comment.id

        #歌曲
        if type == 1:
            music = Music.objects.filter(id=object_id)

            if not music.exists():
                return JsonResponse({'result': 0, 'msg': "音乐不存在"})
            MusicToComment(music_id=object_id, comment_id=comment_id).save()
        #歌单
        elif type == 2:
            musiclist = MusicList.objects.filter(id=object_id)

            if not musiclist.exists():
                return JsonResponse({'result': 0, 'msg': "歌单不存在"})

            MusicListToComplain(musiclist_id=object_id, comment_id=comment_id).save()

        #动态
        elif type == 3:
            post = Post.objects.filter(id=object_id)

            if not post.exists():
                return JsonResponse({'result': 0, 'msg': "动态不存在"})
            PostToComment(post_id=object_id, comment_id=comment_id)


        UserToComment(user_id, comment_id).save()
        return JsonResponse({'result': 1, 'msg': "评论成功"})

    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


def cre_reply(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        root_id = request.POST.get('root_id')
        fa_id = request.POST.get('fa_id')
        isLevel2 = request.POST.get('isLevel2')
        content = request.POST.get('content')

        reply = Reply(replyer_id=user_id,fa_id=fa_id,root_id=root_id,isLevel2=isLevel2,content=content )
        reply.save()

    else:
        return JsonResponse({'result': 0,'msg':"请求方式错误" })


def get_reply(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        root_id = request.GET.get('root_id')
        replys = Reply.objects.filter(root_id=root_id).order_by('-create_date')
        replys = [x.to_dic for x in replys]
        return JsonResponse({
            "result":1,
            "msg":"获取成功",
            "replys":replys,
        })
    else:
        return JsonResponse({'result':0 ,
                             'msg':"请求方式错误"})


#获取所有投诉列表
def list_complain(request):
    if request.method == 'GET':  # 判断请求方式是否为 POST（要求POST方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        if user.is_admin == False:
            result = {'result': 0, 'message': "没有访问权限"}
            return JsonResponse(result)



        complains = Complain.objects.all().order_by('-create_date')
        complains = [x.to_dic() for x in complains]

        return JsonResponse({"result": 1,
                             "msg": "获取成功成功",
                             "music_complain_list": complains})

    else:
        return JsonResponse({'errno': 0, 'msg': "请求方式错误"})


"""
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
"""


#获取对象评论列表
def list_object_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)


        type = request.POST.get("type")
        object_id = request.POST.get("object_id")

        comments = Comment.objects.filter(object_id=object_id, type=type).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#获取用户评论列表
def list_user_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        comments = Comment.objects.filter(poster_id=user_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'result': 1,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


#创建一条信息
def cre_message(poster_id, receiver_id, title, content, message_type, type, object_id):
    new_message = Message(poster_id=poster_id, receiver_id=receiver_id, title=title, content=content,
                          message_type=message_type, type=type, object_id=object_id)
    new_message.save()
    UTM=UserToMessage(user_id=receiver_id, message_id=new_message.id)
    UTM.save()


#当前用户发送消息 系统消息实现，可用通过管理员给用户发消息实现
def send_message(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        if not user.is_admin:
            result = {'result': 0, 'message': "没有访问权限"}
            return JsonResponse(result)

        poster_id = request.POST.get('poster_id')
        receiver_id = request.POST.get('receiver_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        message_type = request.POST.get('message_type')
        type = request.POST.get('type')
        object_id = request.POST.get('object_id')
        cre_message(poster_id=poster_id, receiver_id=receiver_id, title=title, content=content,
            type=type, object_id=object_id,message_type=message_type)


        return JsonResponse({'result': 1,
                             'msg': "消息发送成功"})
    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})





#获取当前用户下的所有消息。
def get_user_message(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)


        messages = Message.objects.filter(receiver_id=user.id).order_by('-create_date')
        messages = [x.to_dic() for x in messages]



        return JsonResponse({'errno': 0,
                             'msg': "获取用户消息成功",
                             'messages': messages
                             })

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#用户删除评论
def del_comment(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        comment_id=request.POST.get('comment_id')
        comment = Comment.objects.filter(id=comment_id)
        comment=comment[0]
        if comment.poster_id != user_id:
            return JsonResponse({'result': 0, 'msg': "不是评论的发出者"})
        comment.delete()

        return JsonResponse({'result': 1, 'msg': "删除成功"})
    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


#用户删除动态
def del_post(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        post_id = request.POST.get('post_id')
        post = Post.objects.filter(id=post_id)
        post = post[0]
        if post.poster_id != user_id:
            return JsonResponse({'result': 0, 'msg': "不是动态的发出者"})
        post.delete()
        PostToComment.objects.filter(post_id=post_id).delete()

        return JsonResponse({'result': 1, 'msg': "删除成功"})
    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


#管理员删除评论、动态
def del_object(request):
    if request.method == 'POST':
        #获取用户信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        #判断是否为管理员
        #用户只能删除自己的对象
        if not user.is_admin:


            result = {'result': 0, 'message': "没有访问权限"}
            return JsonResponse(result)
        #管理员可以删除所有对象
        else:

            object_type = request.POST.get('object_type')




    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})


def verify_code(email, sms_code):
    codes = VerifyCode.objects.filter(email=email , num=sms_code)
    if not codes.exists():
        return 0
    code = codes[0]

    code_time = code.cre_date
    interval_time = (timezone.now().replace(tzinfo=None) - code_time.replace(tzinfo=None)).total_seconds()
    #print(timezone.now().replace(tzinfo=None))
    #print(code_time.replace(tzinfo=None))

    #超时
    if interval_time > 1800:
        return 2
    #正常
    else:
        return 1


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


def send_email_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        sms_code = '%06d' % random.randint(0, 999999)
        #验证码是否已经存在
        if verify_code(email, sms_code) != 0:
            #未超时，不可发送
            if verify_code(email, sms_code) == 1:
                return JsonResponse({'result':0, 'msg':'验证码已发送，请勿短期重复发送'})
            #已超时，删除重发
            elif verify_code(email, sms_code) == 2:
                verify_code = VerifyCode.objects.get(email, sms_code)
                verify_code.delete()

        if send_sms_code(email, sms_code) == 1:
            verify_code = VerifyCode(email=email, num=sms_code)
            verify_code.save()
            return JsonResponse({'result': 1, 'msg': "发送邮件成功"})
        else:
            return JsonResponse({'result': 0, 'msg': "邮件发送异常"})


    else:
        return JsonResponse({'result': 0, 'msg': "请求方式错误"})








