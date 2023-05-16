from datetime import *

from django.db.models import Count
from django.shortcuts import render

from Music.models import Music, Label, MusicList, Singer, SingerToMusic, SingerToAlbum
from User.models import *
from django.http import JsonResponse
from Message.views import verify_code
# Create your views here.
import hashlib
from google.auth import jwt


def check_password(password):
    if not str.isalnum(password):
        return False
    if len(password) < 8 or len(password) > 18:
        return False
    return True


# 加密
def trans_password(password):
    transed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    transed_password = str(transed_password)
    return transed_password



# 注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # 获取请求数据
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        if len(username) == 0 or len(password_1) == 0 or len(password_2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)
        if not check_password(password_1):
            result = {'result': 0, 'message': '密码不合法'}
            return JsonResponse(result)
        if User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': '用户名已存在!'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'result': 0, 'message': '两次密码不一致!'}
            return JsonResponse(result)

        email = request.POST.get('email')
        sms_code = request.POST.get('sms_code')
        if len(email) == 0:
            result = {'result': 0, 'message': '邮箱不允许为空!'}
            return JsonResponse(result)

        # 邮箱验证
        if verify_code(email, sms_code) == 0:
            result = {'result': 0, 'message': '验证码错误，请重新输入'}
            return JsonResponse(result)
        elif verify_code(email, sms_code) == 2:
            result = {'result': 0, 'message': '验证码已失效，请重新获取验证码'}
            return JsonResponse(result)
        if verify_code(email, sms_code) != 0:
            result = {'result': 0, 'message': '未知错误'}
            return JsonResponse(result)

        password = trans_password(password_1)
        user = User(username=username, password=password)
        user.save()

        # 默认给用户创建个人喜爱列表,type 2表示喜欢歌单列表
        like_list = MusicList(creator=user, name=username + '喜爱的歌曲列表', type=2)
        like_list.save()
        user.like_list = like_list
        user.save()

        result = {'result': 1, 'message': '注册成功'}
        return JsonResponse(result)
    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})


# 登录
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # 获取请求数据
        password = request.POST.get('password')

        if len(username) == 0 or len(password) == 0:
            result = {'result': 0, 'message': '用户名与密码不允许为空!'}
            return JsonResponse(result)

        user = User.objects.filter(username=username)
        if not user.exists():  # 判断用户名是否存在
            result = {'result': 0, 'message': '用户名不存在'}
            return JsonResponse(result)
        user = User.objects.get(username=username)
        password = trans_password(password)

        if user.password != password:  # 判断请求的密码是否与数据库存储的密码相同
            result = {'result': 0, 'message': '用户名或密码错误'}
            return JsonResponse(result)

        token = {
            'user_id': user.id,
            'is_admin': user.is_admin
        }
        # JWT令牌
        JWT = jwt.enconde(token, 'secret', algorithm='HS256')
        result = {'result': 1, 'message': "登录成功！", 'JWT': JWT, 'user': user.to_dic_id()}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 修改个人信息
def change_info(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 用户名、性别、所在地、头像、个人简介
        username = request.POST.get('username')
        gender = request.POST.get('gender')
        avatar = request.FILES.get('avatar')
        # TODO 获取头像文件路径并改名存储
        location = request.POST.get('location')
        user.username = username
        user.gender = gender
        user.avatar = avatar
        user.location = location
        user.save()
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 用户上传歌曲
def upload_music(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        file_loc = request.POST.get('file_loc')
        labels = request.POST.get('labels')
        music_name = request.POST.get('music_name')
        music_front = request.FILES.get('music_front')
        description = request.POST.get('description')
        singer_name = request.POST.get('singer_name')

        # TODO 歌曲重名?
        if Music.objects.filter(singer_name=singer_name, music_name=music_name).exists():
            result = {'result': 0, 'message': '歌曲已存在'}
            return JsonResponse(result)

        # 歌手
        if Singer.objects.filter(name=singer_name).exists():
            singer = Singer.objects.get(name=singer_name)
            singer_to_music = SingerToMusic(singer_name=singer_name, music_name=music_name)
            singer_to_music.save()
        else:
            singer = Singer(name=singer_name)
            singer.save()

        music = Music(creator=user, file_loc=file_loc, music_front=music_front,
                      music_name=music_name, description=description, singer=singer)

        # 标签
        # 已经存在就加入
        for label_name in labels:
            if Label.objects.filter(label_name=label_name).exists():
                label = Label.objects.get(label_name=label_name)
                label.label_music.add(music)
                label.save()
            # 不存在就新建标签
            else:
                label = Label(label_name=label_name)
                label.label_music.add(music)
                label.save()

        return JsonResponse({'errno': 0, 'msg': "上传歌曲成功"})
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 用户删除自己上传歌曲
def del_music(request):
    if request.method == 'POST':
        if request.method == 'POST':
            JWT = request.POST.get('JWT')
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录!"}
                return JsonResponse(result)
        music_id = request.POST.get('music_id')
        if Music.objects.filter(id=music_id).exists():
            music = Music.objects.get(id=music_id)
            if music.creator == user:
                # 歌单、专辑、标签中对应歌曲会被删除
                # 删除歌手对应歌曲
                if SingerToMusic.objects.filter(music_id=music_id).exists():
                    SingerToMusic.objects.filter(music_id=music_id).delete()
                music.delete()
                result = {'result': 1, 'message': '歌曲删除成功'}
                return JsonResponse(result)
            else:
                result = {'result': 0, 'message': '无权限删除歌曲'}
                return JsonResponse(result)
        else:
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取个人关注列表的id
def get_follow_list_simple_user(user_id):
    return [x.follow_id for x in UserToFollow.objects.filter(user_id=user_id)]


# 获取个人关注列表的详情(具体信息)
def get_follow_list_detail_user(user_id):
    return [User.objects.get(id=x).to_dic_id() for x in get_follow_list_simple_user(user_id)]


# 获取个人粉丝列表的id
def get_fan_list_simple_user(user_id):
    return [x.fan_id for x in UserToFan.objects.filter(user_id=user_id)]


# 获取个人粉丝列表的详情(具体信息)
def get_fan_list_detail_user(user_id):
    return [User.objects.get(id=x).to_dic_id() for x in get_fan_list_simple_user(user_id)]


# 关注一个用户
def follow(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        # 获取关注用户的实体和id
        follow_id = int(request.POST.get('follow_id'))
        try:
            follow_user = User.objects.get(id=follow_id)
        except Exception as e:
            result = {'result': 0, 'message': "关注的用户不存在!"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id in get_follow_list_simple_user(user_id):
            result = {'result': 0, 'message': "已关注该用户!"}
            return JsonResponse(result)

        # 添加双向记录
        UserToFollow.objects.create(user_id=user_id, follow_id=follow_id)
        UserToFan.objects.create(user_id=follow_id, fan_id=user_id)

        # 关注数+1 , 粉丝数+1
        user.add_follow()
        follow_user.add_fan()

        result = {'result': 1, 'message': "关注成功！"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 取消关注
def unfollow(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)

        # 获取取消关注用户的实体和id
        follow_id = int(request.POST.get('follow_id', ''))
        try:
            follow_user = User.objects.get(id=follow_id)
        except Exception as e:
            result = {'result': 0, 'message': "取消关注的用户不存在!"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id not in get_follow_list_simple_user(user_id):
            result = {'result': 0, 'message': "从未关注过该用户!"}
            return JsonResponse(result)

        # 删除双向记录
        UserToFollow.objects.get(user_id=user_id, follow_id=follow_id).delete()
        UserToFan.objects.get(user_id=follow_id, fan_id=user_id).delete()

        # 关注数-1 , 粉丝数-1
        user.del_follow()
        follow_user.del_fan()

        result = {'result': 1, 'message': "已取消关注此用户！"}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获得用户关注列表
def get_follow_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        result = {'result': 1, 'message': "获取关注列表成功！", "user": user.to_dic_id(),
                  "follow_list": get_follow_list_detail_user(user_id)}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获得用户粉丝列表
def get_fan_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        result = {'result': 1, 'message': "获取粉丝列表成功！", "user": user.to_dic_id(),
                  "fan_list": get_fan_list_detail_user(user_id), }
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取用户创建歌单列表
def get_create_music_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not MusicList.objects.filter(creator_id=user_id).exists():
            result = {'result': 0, 'message': '此用户没有创建歌单'}
            return JsonResponse(result)
        get_music_list = MusicList.objects.filter(creator_id=user_id).all()
        create_music_list = [x.to_dic_id() for x in get_music_list]
        result = {'result': 1, 'message': '获取用户创建歌单成功', 'create_music_list': create_music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取用户喜爱的歌单列表
def get_like_music_list(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            result = {'result': 0, 'message': '不存在该用户'}
            return JsonResponse(result)
        if not UserToLikeMusicList.objects.filter(user_id=user_id).exists():
            result = {'result': 0, 'message': '该用户没有喜爱的歌单'}
            return JsonResponse(result)
        music_list_id = [x.music_list_id for x in UserToLikeMusicList.objects.filter(user_id=user_id).all()]
        like_music_list = [MusicList.objects.get(id=y).to_dic_id() for y in music_list_id]
        result = {'result': 1, 'message': '获取用户喜爱歌单成功', 'like_music_list': like_music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取用户喜爱歌手简单信息
def get_like_singer_simple(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            result = {'result': 0, 'message': '不存在该用户'}
            return JsonResponse(result)
        if not UserToSinger.objects.filter(user_id=user_id).exists():
            result = {'result': 0, 'message': '该用户没有喜爱的歌手'}
            return JsonResponse(result)
        singer_id = [x.singer_id for x in UserToSinger.objects.filter(user_id=user_id).all()]
        like_singer_list = [Singer.objects.get(id=y).to_simple_dic() for y in singer_id]
        result = {'result': 1, 'message': '获取用户喜爱歌手成功', 'like_music_list': like_singer_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 返回最近播放歌曲列表
def get_recent_listen_music_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        max_record = user.max_record
        if not UserListenHistory.objects.filter(user_id=user_id).exists():
            result = {'result': 1, 'message': '此用户目前还没有听歌'}
            return JsonResponse(result)
        history = UserListenHistory.objects.filter(user_id=user_id).all().order_by('-create_date')[:max_record]
        music_list = []
        for music in history:
            music_list.append(music)
        result = {'result': 1, 'message': '成功获取用户最近播放列表', 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 返回用户最近一周/全部时间内听得最多的十首歌
def get_most_listen_music_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        type = request.POST.get('type')
        if type == 1:
            # 先找出该用户最近一周听歌记录
            monday = datetime.today()
            one_day = timedelta(days=-1)
            while monday.weekday() != 0:
                monday += one_day
            listen_history = UserListenHistory.objects.filter(user_id=user_id, create_date__gte=monday). \
                                 values('music_id').annotate(times=Count('music_id')).order_by('-times')[:10]
            if not listen_history.exists():
                result = {'result': 1, 'message': '用户这周还没有听歌记录哦'}
                return JsonResponse(result)
        elif type == 2:
            listen_history = UserListenHistory.objects.filter(user_id=user_id). \
                                 values('music_id').annotate(times=Count('music_id')).order_by('-times')[:10]
            if not listen_history.exists():
                result = {'result': 1, 'message': '用户当前还没有听歌记录哦'}
                return JsonResponse(result)
        else:
            result = {'result': 0, 'message': 'type错误'}
            return JsonResponse(result)
        music_list = []
        for music in listen_history:
            dic = music.to_dic()
            # 增加用户听这首歌的次数
            dic['user_listen_times'] = music.times
            music_list.append(dic)
        if type == 1:
            result = {'result': 1, 'message': '成功获取用户当周听歌历史', 'music_list': music_list}
        else:
            result = {'result': 1, 'message': '成功获取用户当前听歌历史', 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 喜欢歌曲
def like_music(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        user = User.objects.filter(id=user_id)
        # 注册时创建,一定存在
        like_music_list = MusicList.objects.get(creator=user, type=2)
        if like_music_list.music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲已经在您喜爱的歌曲列表中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        like_music_list.music.add(music)
        like_music_list.save()
        result = {'result': 1, 'message': '已成功添加到喜爱歌曲列表'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 创建收藏夹
def create_favorites(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 创建收藏夹需要提供名称 TODO 考虑重名？
        create_name = request.POST.get('create_name')
        user = User.objects.get(id=user_id)
        new_favorites = MusicList(name=create_name,creator=user,type=1)
        description = request.POST.get('description')
        if not description is None:
            new_favorites.description = description
        new_favorites.save()
        result = {'result': 1, 'message': '收藏夹创建成功'}
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取用户当前已经创建的收藏夹
def get_favorites(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        user = User.objects.get(id=user_id)
        if not MusicList.objects.filter(creator=user, type=1).exists():
            result = {'result': 0, 'message': '当前用户未创建收藏夹'}
            return  JsonResponse(result)
        favorites = MusicList.objects.filter(creator=user, type=1).all()
        favorites_list = [x.to_dic_id() for x in favorites]
        result = {'result': 1, 'message': '获取用户收藏夹成功', 'favorites_list': favorites_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 分享歌单
def share_favorites(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 获取要分享的收藏夹
        favorites_id = request.POST.get('favorites_id')
        favorites = MusicList.objects.get(favorites_id)
        labels = request.POST.get('labels')
        if labels is None:
            result = {'result': 0, 'message': '标签不能为空'}
            return JsonResponse(result)
        # 标签
        # 已经存在就加入
        for label_name in labels:
            if Label.objects.filter(label_name=label_name).exists():
                label = Label.objects.get(label_name=label_name)
                label.label_music_list.add(favorites)
                label.save()
            # 不存在就新建标签
            else:
                label = Label(label_name=label_name)
                label.label_music_list.add(favorites)
                label.save()
        music_list_front = request.POST.get('music_list_front')
        if music_list_front is None:
            # 采用默认封面
            pass
        else:
            favorites.music_list_front = music_list_front
        favorites.is_share = True
        favorites.save()
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 收藏歌曲,和喜欢歌曲类似,但要指定歌单/收藏夹
def mark_music(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 要收藏的歌曲id
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        list_id = request.POST.get('music_list_id')
        if not MusicList.objects.filter(id=list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        music_list = MusicList.objects.get(id=list_id)
        if music_list.music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲已在收藏夹中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        music_list.music.add(music)
        music_list.save()
        result = {'result': 1, 'message': '已成功添加到喜爱歌曲列表'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 批量收藏歌曲
def mark_music_list(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 要收藏的歌曲id
        music_list_id = request.POST.get('music_list_id')
        if not MusicList.objects.filter(id=music_list_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        favorites_list_id = request.POST.get('favorites_list_id')
        if not MusicList.objects.filter(id=favorites_list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        music_list = MusicList.objects.get(id=music_list_id)
        favorites_list = MusicList.objects.get(id=favorites_list_id)
        # 遍历收藏指定歌单中的歌曲
        music_s = music_list.music.objects.all()
        for music in music_s:
            music_id = music.id
            # 不存在则收藏
            # TODO 重复收藏是否报错？
            if not favorites_list.music.objects.filter(id=music_id).exists():
                favorites_list.music.add(music)
                favorites_list.save()
        result = {'result': 1, 'message': '已成功收藏歌单'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)