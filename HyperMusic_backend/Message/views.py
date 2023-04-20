from django.http import JsonResponse
from django.shortcuts import render
from Message.models import UserToComment, UserToComplain, MusicToComment, Comment, MusicToComplain, Complain
from User.models import User


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

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_complain_list': complains})

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

        comments = Comment.objects.filter(music_id=music_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


#获取用户评论列表
def list_user_comment(request):
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

        comments = Comment.objects.filter(music_id=music_id).order_by('-create_date')
        comments = [x.to_dic() for x in comments]

        return JsonResponse({'errno': 0,
                             'msg': "获取成功成功",
                             'music_comment_list': comments})

    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


