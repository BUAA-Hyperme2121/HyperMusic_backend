import json
import random
from datetime import datetime

import jwt
from django.core.mail import send_mail
from django.http import JsonResponse
from Music.models import *
from Message.models import *
from User.models import User,UserToFollow
from django.utils import timezone


def get_follow_list_simple_user(user_id):
    return [x.follow_id for x in UserToFollow.objects.filter(user_id=user_id)]


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


# 动态 -1 评论 -2 回复 - 3
def like(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT','-1')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        user_id = user_id
        object_id = request.POST.get("object_id", '-1')
        type = request.POST.get("type",'-1')
        like = Likes(user_id=user_id, object_id=object_id, type=type)
        like.save()
        if type == '1':
            post=Post.objects.get(id=object_id)
            post.like_num += 1
            post.save()
        elif type == '2':
            comment = Comment.objects.get(id=object_id)
            comment.like_num +=1
            comment.save()
        elif type == '3':
            reply = Reply.objects.get(id=object_id)
            reply.like_num +=1
            reply.save()

        return JsonResponse({'result': 1, 'message': "点赞成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})

def cancel_like(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT','-1')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        user_id = user_id
        object_id = request.POST.get("object_id", '-1')
        type = request.POST.get("type",'-1')
        #消除点赞关系
        like = Likes.objects.filter(user_id=user_id, object_id=object_id, type=type)
        if not like.exists():
            result = {'result': 0, 'message': "未点赞"}
            return JsonResponse(result)
        like.delete()
        #减少对象点赞数
        if type == '1':
            post = Post.objects.get(id=object_id)
            post.like_num-=1
            post.save()
        elif type == '2':
            comment = Comment.objects.get(id=object_id)
            comment.like_num-=1
            comment.save()
        elif type == '3':
            reply = Reply.objects.get(id=object_id)
            reply.like_num -= 1
            reply.save()

        return JsonResponse({'result': 1, 'message': "取消点赞成功"})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})

#投诉种类 1 为歌曲 2为歌单
def cre_complain(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        # 从数据库获取用户
        JWT = request.POST.get('JWT','-1')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)



        user_id = user.id
        object_id = request.POST.get("object_id",'')
        content = request.POST.get("content",'')
        type = request.POST.get("type",'')
        title = request.POST.get("title", '')


        new_complain = Complain(poster_id=user_id, object_id=object_id, content=content, type=type, state=1,title=title)
        new_complain.save()
        complain_id = new_complain.id
        #存储外表关系

        UserToComplain(user_id, complain_id).save()

        # 投诉类型为音乐


        if type == '1':
            music=Music.objects.filter(id=object_id)

            if not music.exists():
                return JsonResponse({'result': 0, 'message': "音乐不存在"})
            MusicToComplain(music_id=object_id, complain_id=complain_id).save()
        # 投诉类型为歌单

        elif type == '2':

            musiclist = MusicList.objects.filter(id=object_id)
            print(musiclist)
            if not musiclist.exists():
                return JsonResponse({'result': 0, 'message': "歌单不存在"})
            MusicListToComplain(musiclist_id=object_id, complain_id=complain_id).save()

        return JsonResponse({
                            'result': 0,
                            'message': "投诉成功",
                            'state':new_complain.state,
                             })

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


#0 是音乐 1 是歌单 2 是动态
def cre_comment(request):
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）

        JWT = request.POST.get('JWT','-1')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)


        object_id = request.POST.get("object_id", '-1')
        content = request.POST.get("content", '-1')
        type = request.POST.get("type", '-1')

        new_comment = Comment(poster_id=user_id, object_id=object_id, content=content, type=type)
        new_comment.save()
        comment_id = new_comment.id

        #歌曲
        if type == '1':
            music = Music.objects.filter(id=object_id)

            if not music.exists():
                return JsonResponse({'result': 0, 'message': "音乐不存在"})
            MusicToComment(music_id=object_id, comment_id=comment_id).save()
        #歌单
        elif type == '2':
            musiclist = MusicList.objects.filter(id=object_id)

            if not musiclist.exists():
                return JsonResponse({'result': 0, 'message': "歌单不存在"})

            MusicListToComplain(musiclist_id=object_id, comment_id=comment_id).save()

        #动态
        elif type == '3':
            post = Post.objects.filter(id=object_id)

            if not post.exists():
                return JsonResponse({'result': 0, 'message': "动态不存在"})
            PostToComment(post_id=object_id, comment_id=comment_id)


        UserToComment(user_id, comment_id).save()
        return JsonResponse({'result': 1, 'message': "评论成功", "comment": new_comment.to_dic()})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def cre_post(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        poster_id = user_id
        content = request.POST.get('content','-1')
        type = request.POST.get('type','-1')
        object_id = request.POST.get('object_id','-1')
        post = Post(poster_id=poster_id, content=content, type=type, object_id=object_id)
        post.save()
        user.post_num+=1
        user.save()
        return JsonResponse({"result": 1, "message": "创建动态成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


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
        return JsonResponse({'result': 1,'message':"创建回复成功" })
    else:
        return JsonResponse({'result': 0,'message':"请求方式错误" })


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
        tmp = replys
        replys = []
        for x in tmp:
            dict = x.to_dic()
            like = Likes.objects.filter(user_id=user_id, type=3,object_id=dict['id'])
            if like.exists():
                dict['is_liked'] = 1
            else:
                dict['is_liked'] = 0
            replys.append(dict)

        return JsonResponse({
            "result": 1,
            "message": "获取成功",
            "replys": replys,
        })
    else:
        return JsonResponse({'result':0 ,
                             'message':"请求方式错误"})


#获取所有投诉列表
def list_complain(request):
    if request.method == 'GET':  # 判断请求方式是否为 POST（要求POST方式）
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        if user.is_admin == False:
            result = {'result': 0, 'message': "没有访问权限"}
            return JsonResponse(result)



        complains = Complain.objects.all().order_by('-create_date')
        complains = [x.to_dic() for x in complains]

        return JsonResponse({"result": 1,
                             "message": "获取成功成功",
                             "music_complain_list": complains})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})



#获取用户投诉列表
def list_user_complain(request):
    if request.method == 'GET':  # 判断请求方式是否为 POST（要求POST方式）
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        # 从数据库获取用户

        complains = Complain.objects.filter(poster_id=user_id).order_by('-create_date')
        complains = [x.to_dic() for x in complains]

        return JsonResponse({'errno': 0,
                             'message': "获取当前用户成功",
                             'music_complain_list': complains})

    else:
        return JsonResponse({'errno': 1001, 'message': "请求方式错误"})



#获取对象评论列表
def list_object_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)


        type = request.GET.get("type")
        object_id = request.GET.get("object_id")

        comments = Comment.objects.filter(object_id=object_id, type=type).order_by('-create_date')

        tmp = comments
        comments = []
        for x in tmp:
            dict = x.to_dic()

            like = Likes.objects.filter(user_id=user_id, type=2, object_id=dict.get('id'))
            if like.exists():
                dict['is_liked'] = 1
            else:
                dict['is_liked'] = 0
            comments.append(dict)
        return JsonResponse({'result': 0,
                             'message': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


#获取用户评论列表
def list_user_comment(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.GET.get('JWT')
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
                             'message': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


#创建一条信息
def cre_message(poster_id, receiver_id, title, content, message_type, type, object_id, from_object_id=0):
    new_message = Message(poster_id=poster_id, receiver_id=receiver_id, title=title, content=content,
                          message_type=message_type, type=type, object_id=object_id, from_object_id=from_object_id)
    new_message.save()
    UTM=UserToMessage(user_id=receiver_id, message_id=new_message.id)
    UTM.save()


def get_follow_post(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        #获取当前用户的关注列表
        followers = get_follow_list_simple_user(user_id)
        #获取关注用户所有动态
        follower_posts =[]
        #遍历每个用户id
        for follower_id in followers:
            posts = Post.objects.filter(poster_id=follower_id)
            posts = [x.to_dic() for x in posts]
            #获取此用户下的所有动态，添加读状态
            for x in posts:
                if Likes.objects.filter(user_id=user_id, type=1, object_id=x['id']).exists():
                    x['is_liked'] = 1
                else:
                    x['is_liked'] = 0
                follower_posts.append(x)
        #按日期降序排序
        follower_posts = sorted(follower_posts, key=lambda i: i['create_date'], reverse=True)
        return JsonResponse({'result':1, 'message':"获取成功", 'posts':follower_posts})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def get_user_post(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT')
        if JWT != -1:
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录!"}
                return JsonResponse(result)
        else:
            user_id = -1
        #获取访问空间用户的id
        spaceuser_id = request.GET.get('user_id')
        #获取空间用户的动态
        posts = Post.objects.filter(poster_id=spaceuser_id)
        posts = [x.to_dic() for x in posts]
        tmp = posts
        posts = []
        #添加当前登录用户是否点赞状态
        for x in tmp:
            if Likes.objects.filter(user_id=user_id, type=1, object_id=x['id']).exists():
                x['is_liked'] = 1
            else:
                x['is_liked'] = 0
            posts.append(x)

        return JsonResponse({'result': 1,'message':"获取用户下的动态成功",'posts':posts})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})





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

        poster_id = request.POST.get('poster_id')
        receiver_id = request.POST.get('receiver_id')
        title = request.POST.get('title')
        content = request.POST.get('content')
        message_type = request.POST.get('message_type')
        type = request.POST.get('type')
        object_id = request.POST.get('object_id')
        from_object_id = request.POST.get('from_object_id', '0')

        cre_message(poster_id=poster_id, receiver_id=receiver_id, title=title, content=content,
            type=type, object_id=object_id,message_type=message_type, from_object_id=from_object_id)


        return JsonResponse({'result': 1, 'message': "消息发送成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})





#获取当前用户下的所有消息。
def get_user_message(request):
    if request.method == 'GET':  # 判断请求方式是否为 GET（要求GET方式）
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)


        messages = Message.objects.filter(receiver_id=user.id).order_by('-create_date')
        messages = [x.to_dic() for x in messages]



        return JsonResponse({'result': 1,
                             'message': "获取用户消息成功",
                             'messages': messages
                             })

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


#用户删除评论
def del_comment(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        comment_id=request.GET.get('comment_id')
        comment = Comment.objects.filter(id=comment_id)
        comment=comment[0]
        if comment.poster_id != user_id:
            return JsonResponse({'result': 0, 'message': "不是评论的发出者"})
        comment.delete()

        return JsonResponse({'result': 1, 'message': "删除成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def modify_comment(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        comment_id=request.GET.get('comment_id')
        content=request.GET.get('content')
        comment = Comment.objects.filter(id=comment_id)
        comment=comment[0]
        if comment.poster_id != user_id:
            return JsonResponse({'result': 0, 'message': "不是评论的发出者"})
        comment.content = content
        comment.save()

        return JsonResponse({'result': 1, 'message': "修改评论成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


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
            return JsonResponse({'result': 0, 'message': "不是动态的发出者"})
        post.delete()
        PostToComment.objects.filter(post_id=post_id).delete()

        return JsonResponse({'result': 1, 'message': "删除成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


#管理员删除 1 - 评论、2 - 动态
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

            object_type = request.POST.get('type')
            object_id = request.POST.get('object_id')
            #删除评论

            if object_type == '1':
                #删除评论本身
                comment =  Comment.objects.get(id=object_id)
                comment.delete()
                # 删除评论下的所有回复
                replys = Reply.objects.filter(root_id=object_id)
                replys.delete()

                return JsonResponse({'result': 1, 'message': "删除评论成功"})
            #删除动态
            elif object_type == '2':
                post = Post.objects.get(id=object_id)
                post.delete()
                # 删除动态下的评论
                comments = Comment.objects.filter(type=3, object_id=object_id)
                comments.delete()
                # 删除评论下的所有回复
                replys = Reply.objects.filter(root_id=object_id)
                replys.delete()
                return JsonResponse({'result': 1, 'message': "删除动态成功"})
            #删除回复
            elif object_type == '3':

                # 删除评论下的所有回复
                replys = Reply.objects.filter(id=object_id)
                replys.delete()
                return JsonResponse({'result': 1, 'message': "删除回复成功"})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


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
    #if interval_time > 1800:
    #    return 2
    #正常
    #else:
    return 1



def send_sms_code(html ,to_email, title, sms_code):
    """
    发送邮箱验证码
    :param to_mail: 发到这个邮箱
    :return: 成功：0 失败 -1
    """
    # 生成邮箱验证码
    data = {'sms_code': sms_code }
    html_content=render_to_string(html, data)

    EMAIL_FROM = "2522820243@qq.com"  # 邮箱来自
    email_title = title

    msg = EmailMessage(email_title,
                       html_content,
                       EMAIL_FROM,
                       [to_email])

    msg.content_subtype = 'html'
    send_status = msg.send()

    return send_status


def send_email_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        sms_code = '%06d' % random.randint(0, 999999)

        #验证码是否已经存在
        if verify_code(email, sms_code) != 0:

            #未超时，不可发送
            if verify_code(email, sms_code) == 1:
                return JsonResponse({'result':0, 'message':'验证码已发送，请勿短期重复发送'})
            #已超时，删除重发
            elif verify_code(email, sms_code) == 2:
                code = VerifyCode.objects.get(email, sms_code)
                code.delete()
        title='欢迎注册HyperMuisc音乐平台'
        content="您的邮箱注册验证码为：{0}, 该验证码有效时间为三十分钟，请及时进行验证。".format(sms_code)
        try:
            res = send_sms_code('email_register.html', email, title, sms_code,)
        except Exception as e:
            print(e)
            return JsonResponse({'result':0, 'message':"邮箱错误"})

        if res == 1:
            code = VerifyCode(email=email, num=sms_code)
            code.save()
            return JsonResponse({'result': 1, 'message': "发送邮件成功"})
        else:
            return JsonResponse({'result': 0, 'message': "邮件发送异常"})


    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def send_email_find_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        sms_code = '%06d' % random.randint(0, 999999)

        #验证码是否已经存在
        if verify_code(email, sms_code) != 0:

            #未超时，不可发送
            if verify_code(email, sms_code) == 1:
                return JsonResponse({'result':0, 'message':'验证码已发送，请勿短期重复发送'})
            #已超时，删除重发
            elif verify_code(email, sms_code) == 2:
                code = VerifyCode.objects.get(email, sms_code)
                code.delete()
        title='这是一封来自Hypermusic的邮件，帮助你找回密码'

        try:
            res = send_sms_code('email_findpassword.html', email, title, sms_code)
        except Exception as e:
            return JsonResponse({'result':0, 'message':"邮箱错误"})

        if res == 1:
            code = VerifyCode(email=email, num=sms_code)
            code.save()
            return JsonResponse({'result': 1, 'message': "发送邮件成功"})
        else:
            return JsonResponse({'result': 0, 'message': "邮件发送异常"})


    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})




def audit(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        if user.is_admin == False:
            return JsonResponse({"result":0,'message': "没有访问权限"})
        complain_id = request.POST.get('complain_id')
        complain = Complain.objects.filter(id=complain_id)
        if not complain.exists():
            return JsonResponse({'result':0, 'message':"数据库中不存在相应投诉"})
        result = request.POST.get('result')
        reason = request.POST.get('reason')

        complain = complain[0]
        complain.audit_time = datetime.now()
        complain.state = 2
        complain.result = result
        complain.reason = reason
        complain.save()


        #审核通关
        if result == '1':

            return JsonResponse({'result':1,'message':"审核结果为：通过"})

        #审核未通过,改变文件为不可见

        elif result == '2':
            type = complain.type

            object_id = complain.object_id
            #删除音乐
            if type == '1':
                music = Music.objects.get(id=object_id)
                music.delete()

            #隐藏歌单
            elif type == '2':
                musiclist = MusicList.objects.get(id=object_id)
                musiclist.is_public = False
                musiclist.save()


            return JsonResponse({'result':1, 'message':"审核结果为：不通过"})
    else:
        return JsonResponse({'result':0, 'message':"请求方式错误"})


def get_complain_detail(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT')
        print(JWT)
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])

            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)



        complain_id = request.GET.get('complain_id')
        complain = Complain.objects.get(id=complain_id)
        if user.is_admin == False and user.id != complain.poster_id:
            result = {'result': 0, 'message': "没有访问权限"}
            return JsonResponse(result)

        return JsonResponse({'result':1, 'complain': complain.to_dic_detail(),'message':"获取投诉成功"})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})
        

def ai_audit(request):
    if request.method == 'POST':

        body = json.loads(request.body)
        if body.get('JobsDetail') is None:
            return {'result': 0,'message':"审核返回结果异常"}
        else:
            result = body.get('JobsDetail').get('Result')
            label = body.get('JobsDetail').get('Label')
            job_id = body.get('JobsDetail').get('JobId')
            print(job_id)
            job = JobToMusic.objects.filter(job_id=job_id)
            music_id = job[0].music_id
            music = Music.objects.get(id=music_id)
            #审核通过
            if result == 0:
                music.is_audit = True
                music.save()
                return JsonResponse({"message":"通过审核",'job_id':job_id})
            #TODO 审核未通过
            else:
                Message(title="音乐审核未通过", receiver_id=music.creator.id, content="你上传的歌曲"+ music.music_name +"审核未通过，已经删除", message_type=5).save()
                return JsonResponse({"message": "未通过审核，上传视频删除", 'job_id': job_id})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def get_user_reply(request):
    if request.method == "GET":
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])

            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        comments = Comment.objects.filter(poster_id=user_id)
        replys= Reply.objects.filter(root_id=-114514)
        for x in comments:
            replys = (replys | Reply.objects.filter(root_id=x.id))

        replys = [x.to_dic() for x in replys]
        return JsonResponse({'result':1, 'message':"请求成功", "replys":replys})
    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def set_read(request):
    if request.method == "POST":
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])

            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        message_id = request.POST.get('message_id')
        message = Message.objects.get(id=message_id)
        message.state = 1
        message.save()
        return JsonResponse({'result': 1, 'message': "设置消息已读成功"})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def set_read_all(request):
    if request.method == "POST":
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])

            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        messages = Message.objects.filter(receiver_id=user_id)
        messages.update(state=1)

        return JsonResponse({'result': 1, 'message': "设置消息已读成功"})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})


def get_unread_num(request):

    if request.method == "GET":
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])

            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            print(e)
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        messages = Message.objects.filter(receiver_id=user_id, state=0)
        num = messages.count()
        return JsonResponse({'result': 1, 'message': "成功获取未读消息数量", "unread_num":num})

    else:
        return JsonResponse({'result': 0, 'message': "请求方式错误"})