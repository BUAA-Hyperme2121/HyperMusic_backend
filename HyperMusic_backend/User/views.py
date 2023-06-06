# Create your views here.
import hashlib
from datetime import *
from random import Random

import jwt
from django.db.models import Count
from django.http import JsonResponse

from Bucket import *
from HyperMusic_backend.settings import MEDIA_ROOT
from Message.views import verify_code, JobToMusic
from Music.models import Music, Label, MusicList, SingerToMusic
from User.models import *

# 歌单默认标签
music_list_labels = ['怀旧', '浪漫', '伤感', '放松', '治愈']
# 歌曲默认标签
music_labels = ['流行', '摇滚', '民谣', '电子', '说唱', '轻音乐', '古风', '爵士', '金属', '拉丁']
# 歌手默认标签
singer_labels = ['华语男歌手', '华语女歌手', '华语乐队',
                 '欧美男歌手', '欧美女歌手', '欧美乐队',
                 '日韩男歌手', '日韩女歌手', '日韩乐队']


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


def create_code(random_length=8):
    str_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str_code += chars[random.randint(0, length)]
    return str_code


# 注册
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        if len(username) == 0 or len(password_1) == 0 or len(password_2) == 0:
            result = {'result': 0, 'message': '用户名与密码不允许为空'}
            return JsonResponse(result)
        if not check_password(password_1):
            result = {'result': 0, 'message': '密码不合法'}
            return JsonResponse(result)
        if User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': '用户名已存在'}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {'result': 0, 'message': '两次密码不一致!'}
            return JsonResponse(result)

        email = request.POST.get('email')
        sms_code = request.POST.get('sms_code')
        if len(email) == 0:
            result = {'result': 0, 'message': '邮箱不允许为空'}
            return JsonResponse(result)

        # 邮箱验证
        if verify_code(email, sms_code) == 0:
            result = {'result': 0, 'message': '验证码错误，请重新输入'}
            return JsonResponse(result)
        elif verify_code(email, sms_code) == 2:
            result = {'result': 0, 'message': '验证码已失效，请重新获取验证码'}
            return JsonResponse(result)
        if verify_code(email, sms_code) != 1:
            result = {'result': 0, 'message': '未知错误'}
            return JsonResponse(result)

        password = trans_password(password_1)
        user = User(username=username, password=password)
        user.save()
        # 默认给用户创建个人喜爱列表,type 2表示喜欢歌单列表
        like_list = MusicList(creator=user, name=username + '喜爱的歌曲列表', type=2)
        like_list.save()
        user.like_list = like_list.id
        user.save()

        result = {'result': 1, 'message': '注册成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


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
        JWT = jwt.encode(token, 'secret', algorithm='HS256')
        result = {'result': 1, 'message': "登录成功", 'JWT': JWT, 'user': user.to_dic()}
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
        username = request.POST.get('username', '')
        if len(username) == 0:
            result = {'result': 0, 'message': '用户名不允许为空'}
            return JsonResponse(result)
        if username != user.username:
            if User.objects.filter(username=username).exists():
                result = {'result': 0, 'message': '用户名已存在'}
                return JsonResponse(result)

        avatar = request.FILES.get('avatar', None)
        # 获取头像文件路径并改名存储
        if avatar:
            suffix = '.' + avatar.name.split('.')[-1]
            avatar.name = 'avatar' + str(user.id) + suffix

            # 临时保存到本地
            avatar_dir = os.path.join(MEDIA_ROOT, avatar.name)
            with open(avatar_dir, 'wb+') as destination:
                for chunk in avatar.chunks():
                    destination.write(chunk)

            bucket = Bucket()
            key = create_code()

            # 上传审核
            upload_result = bucket.upload_file('hypermusic', avatar.name, avatar.name)
            if upload_result == -1:
                os.remove(avatar_dir)
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('hypermusic', avatar.name)
            if audit_dic.get('result') != 0:
                bucket.delete_object('hypermusic', avatar.name)
                os.remove(avatar_dir)
                result = {'result': 0, 'message': '审核不通过', 'user': user.to_dic()}
                return JsonResponse(result)

            # TODO 判断是否默认头像，若不是，删除以前存储的，否则存储名重复

            # 获取存储路径
            avatar_path = bucket.query_object('hypermusic', avatar.name)
            if not avatar_path:
                os.remove(avatar_dir)
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            user.avatar_path = avatar_path
            user.save()
            os.remove(avatar_dir)

        location = request.POST.get('location', '')
        gender = request.POST.get('gender', '')
        introduction = request.POST.get('introduction','')
        if len(gender) == 0:
            gender = '未知'
        if len(introduction) == 0:
            introduction = '这个人很懒，什么都没有留下'
        if len(location) == 0:
            location = '未知'
        user.username = username
        user.gender = gender
        user.location = location
        user.introduction = introduction
        user.save()

        result = {'result': 1, 'message': '修改个人信息成功'}
        return JsonResponse(result)
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

        labels_music = request.POST.getlist('music_labels', '')
        music_name = request.POST.get('music_name', '')
        music_cover = request.FILES.get('music_cover', None)
        description = request.POST.get('description', '')
        singer_name = request.POST.get('singer_name', '')
        lyrics = request.FILES.get('lyrics', None)

        if music_name == '' or labels_music == '' or singer_name == '':
            result = {'result': 0, 'message': '歌曲名称或歌曲标签或创作歌手不能为空'}
            return JsonResponse(result)

        if len(music_name) > 100:
            result = {'result': 0, 'message': '歌曲名过长'}
            return JsonResponse(result)

        # 音源文件不存在
        music_upload = request.FILES.get('music', None)

        if not music_upload:
            result = {'result': 0, 'message': '上传歌曲不能为空'}
            return JsonResponse(result)

        # 设置歌手,有就记录,无就新建
        if not Singer.objects.filter(name=singer_name).exists():
            singer = Singer(name=singer_name)
            singer.save()
        singer = Singer.objects.get(name=singer_name)
        singer_id = singer.id

        # 歌曲为同一上传者同一歌手的同名歌曲，不能重复
        if Music.objects.filter(singer=singer, creator=user, music_name=music_name).exists():
            result = {'result': 0, 'message': '歌曲已存在'}
            return JsonResponse(result)

        music = Music(music_name=music_name, description=description, creator=user, singer=singer)
        music.save()

        bucket = Bucket()

        music_id = music.id
        suffix_music_cover = ''
        # 如果用户上传了封面
        if music_cover:
            if music_cover.size > 2 * 1024 * 1024:
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '封面大小不能超过2M'}
                return JsonResponse(result)
            # 后缀为上传歌曲的后缀
            suffix_music_cover = '.' + music_cover.name.split('.')[-1]
            # 修改封面文件流对象的名称
            music_cover.name = 'cover' + str(music_id) + suffix_music_cover

            # 临时保存到本地
            music_cover_dir = os.path.join(MEDIA_ROOT, music_cover.name)

            with open(music_cover_dir, 'wb+') as destination:
                for chunk in music_cover.chunks():
                    destination.write(chunk)
                destination.close()

            # 上传封面
            upload_result = bucket.upload_file('hypermusic', music_cover.name, music_cover.name)

            if upload_result == -1:
                # 删除歌曲对象
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '上传失败'}
                # 删除本地存储
                os.remove(music_cover_dir)
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('hypermusic', music_cover.name)

            if audit_dic.get('result') != 0:
                bucket.delete_object('hypermusic', music_cover.name)
                Music.objects.get(id=music_id).delete()
                os.remove(music_cover_dir)
                result = {'result': 0, 'message': '歌曲封面审核失败'}
                return JsonResponse(result)

            # 获取存储路径
            music_cover_path = bucket.query_object('hypermusic', music_cover.name)
            if not music_cover_path:
                Music.objects.get(id=music_id).delete()
                singer.delete()
                os.remove(music_cover_dir)
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            music.cover_path = music_cover_path
            music.save()
            # 删除本地文件
            os.remove(music_cover_dir)

        # 上传歌曲
        if music_upload.size > 1024 * 1024 * 20:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('hypermusic', music_cover.name)
            Music.objects.get(id=music_id).delete()
            singer.delete()
            result = {'result': 0, 'message': '音频大小不能超过20M'}
            return JsonResponse(result)

        suffix_music = '.' + music_upload.name.split('.')[-1]
        music_upload.name = "music" + str(music_id) + suffix_music

        # 临时保存到本地
        music_upload_dir = os.path.join(MEDIA_ROOT, music_upload.name)
        with open(music_upload_dir, 'wb+') as destination:
            for chunk in music_upload.chunks():
                destination.write(chunk)
        # 上传音乐
        upload_result = bucket.upload_file('hypermusic', music_upload.name, music_upload.name)
        if upload_result == -1:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('hypermusic', music_cover.name)
            Music.objects.get(id=music_id).delete()
            singer.delete()
            os.remove(music_upload_dir)
            result = {'result': 0, 'message': '上传歌曲失败'}
            return JsonResponse(result)
        # 上传是否可以获得路径
        music_path = bucket.query_object('hypermusic', music_upload.name)
        if not music_path:
            if music.cover_path != '':
                bucket.delete_object('hypermusic', music_cover.name)
            Music.objects.get(id=music_id).delete()
            singer.delete()
            os.remove(music_upload_dir)
            result = {'result': 0, 'message': '上传歌曲失败'}
            return JsonResponse(result)

        # 获取桶存储路径成功
        music.music_path = music_path
        music.save()
        # 删除本地文件
        os.remove(music_upload_dir)
        # 审核音乐
        audit_dic = bucket.music_audit_submit('hypermusic', music_upload.name)
        jobid = audit_dic.get('job_id')
        # 查询审核结果

        if audit_dic.get('result') != 1:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('hypermusic', music_cover.name)
            # 删除音乐
            bucket.delete_object('hypermusic', music_upload.name)
            Music.objects.get(id=music_id).delete()
            singer.delete()
            result = {'result': 0, 'message': '歌曲自动审核失败'}
            return JsonResponse(result)
        JobToMusic(job_id=jobid, music_id=music_id).save()

        # TODO 设置歌手默认封面,歌曲默认封面

        # 处理用户上传歌词
        if lyrics:
            suffix_lyrics = '.' + lyrics.name.split('.')[-1]
            lyrics.name = "lyrics" + str(music_id) + suffix_lyrics

            # 临时保存到本地
            lyrics_dir = os.path.join(MEDIA_ROOT, lyrics.name)
            with open(lyrics_dir, 'wb+') as destination:
                for chunk in lyrics.chunks():
                    destination.write(chunk)

            upload_result = bucket.upload_file('hypermusic', lyrics.name, lyrics.name)
            if upload_result == -1:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('hypermusic', music_cover.name)
                bucket.delete_object('hypermusic', music_upload.name)

                # 删除歌手封面
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()

                # 删除本地文件
                os.remove(lyrics_dir)
                result = {'result': 0, 'message': '上传歌词失败'}
                return JsonResponse(result)

            # 是否可以获取路径
            lyrics_path = bucket.query_object('hypermusic', lyrics.name)
            if not lyrics_path:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('hypermusic', music_upload.name)
                bucket.delete_object('hypermusic', music_cover.name)

                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(name=singer_name).delete()
                # 删除本地文件
                os.remove(lyrics_dir)
                result = {'result': 0, 'message': '上传歌词失败'}
                return JsonResponse(result)
            music.lyrics_path = lyrics_path
            music.save()
            # 删除本地文件
            os.remove(lyrics_dir)

        # 判断是否原创歌曲
        if user.username == singer_name:
            music.is_original = True
            music.save()
        print(music.id)
        # 歌曲标签
        for label_name in labels_music:
            if label_name not in music_labels:
                label_name = '其他'
            if Label.objects.filter(label_name=label_name).exists():
                label = Label.objects.get(label_name=label_name)
                label.label_music.add(music)
                label.save()
            # 不存在就新建标签
            else:
                label = Label(label_name=label_name)
                label.save()
                label.label_music.add(music)
                label.save()

        # 歌手不上传标签,贴上其他
        label_name = '其他歌手或乐队'
        if Label.objects.filter(label_name=label_name).exists():
            label = Label.objects.get(label_name=label_name)
            label.label_singer.add(singer)
            label.save()
        # 不存在就新建标签
        else:
            label = Label(label_name=label_name)
            label.save()
            label.label_singer.add(singer)
            label.save()

        # 最后成功再添加歌手与歌曲关系
        singer_to_music = SingerToMusic(singer_id=singer_id, music_id=music_id)
        singer_to_music.save()

        result = {'result': 1, 'message': '上传歌曲成功,请耐心等待审核通过'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 用户删除自己上传歌曲
def del_music(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id', '')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定要删除歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        if music.creator != user:
            result = {'result': 0, 'message': '无权限删除歌曲'}
            return JsonResponse(result)
        # 删除桶对象
        bucket = Bucket()
        # 删除封面（上传的或默认的）
        suffix_music_cover = '.' + music.cover_path.split('.')[-1]
        bucket.delete_object('hypermusic', 'cover' + str(music_id) + suffix_music_cover)
        if music.lyrics_path != '':
            # 删除歌词
            suffix_lyrics = '.' + music.lyrics_path.split('.')[-1]
            bucket.delete_object('hypermusic', 'lyrics' + str(music_id) + suffix_lyrics)
        # 删除音源
        suffix_music = '.' + music.music_path.split('.')[-1]
        bucket.delete_object('hypermusic', 'music' + str(music_id) + suffix_music)
        # 删除用户听歌记录
        UserListenHistory.objects.filter(music_id=music_id).delete()
        # 删除歌手对应歌曲
        SingerToMusic.objects.filter(music_id=music_id).delete()
        # 歌曲删除后,歌单、标签中对应歌曲会被删除,但歌单中需要相应的减少数量
        music_list = MusicList.objects.all()
        for ml in music_list:
            if ml.music.filter(id=music_id).exists():
                ml.music.remove(music)
                ml.del_music()
                ml.save()
        # 删除用户听歌记录
        UserListenHistory.objects.filter(music_id=music_id).delete()
        # 删除歌曲对象本身
        music.delete()
        result = {'result': 1, 'message': '歌曲删除成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 获取个人关注列表的id
def get_follow_list_simple_user(user_id):
    return [x.follow_id for x in UserToFollow.objects.filter(user_id=user_id)]


# 获取个人关注列表的详情(具体信息)
def get_follow_list_detail_user(user_id):
    return [User.objects.get(id=x).to_dic() for x in get_follow_list_simple_user(user_id)]


# 获取个人粉丝列表的id
def get_fan_list_simple_user(user_id):
    return [x.fan_id for x in UserToFan.objects.filter(user_id=user_id)]


# 获取个人粉丝列表的详情(具体信息)
def get_fan_list_detail_user(user_id):
    return [User.objects.get(id=x).to_dic() for x in get_fan_list_simple_user(user_id)]


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
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)

        # 获取关注用户的实体和id
        follow_id = int(request.POST.get('follow_id', ''))
        if follow_id == user_id:
            result = {'result': 0, 'message': '你时时刻刻都在关注你自己~'}
            return JsonResponse(result)
        try:
            follow_user = User.objects.get(id=follow_id)
        except Exception as e:
            result = {'result': 0, 'message': "要关注的用户不存在"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id in get_follow_list_simple_user(user_id):
            result = {'result': 0, 'message': "已关注该用户"}
            return JsonResponse(result)

        # 添加双向记录
        UserToFollow.objects.create(user_id=user_id, follow_id=follow_id)
        UserToFan.objects.create(user_id=follow_id, fan_id=user_id)

        # 关注数+1 , 粉丝数+1
        user.add_follow()
        follow_user.add_fan()

        result = {'result': 1, 'message': "关注成功"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 取消关注
def unfollow(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
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
            result = {'result': 0, 'message': "要取消关注的用户不存在!"}
            return JsonResponse(result)

        # 是否已关注
        if follow_id not in get_follow_list_simple_user(user_id):
            result = {'result': 0, 'message': "从未关注过该用户"}
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
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        user = None
        if JWT != '-1':
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        get_user_id = request.GET.get('user_id')
        follow_list_get = get_follow_list_simple_user(get_user_id)
        follow_list = []
        if len(follow_list_get) != 0:
            for id in follow_list_get:
                dic = User.objects.get(id=id).to_dic()
                dic['is_follow'] = False
                # 当前用户为登录用户
                if user:
                    if UserToFollow.objects.filter(user_id=user.id, follow_id=id).exists():
                        dic['is_follow'] = True
                follow_list.append(dic)
        result = {'result': 1, 'message': "获取关注列表成功", "user": user.to_dic() if user else {},
                  "follow_list": follow_list, }
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获得用户粉丝列表
def get_fan_list(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        user = None
        if JWT != "-1":
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        get_user_id = request.GET.get('user_id')
        fan_list_get = get_fan_list_simple_user(get_user_id)
        fan_list = []
        if len(fan_list_get) != 0:
            for id_ in fan_list_get:
                dic = User.objects.get(id=id_).to_dic()
                dic['is_follow'] = False
                # 当前用户为登录用户
                if user:
                    if UserToFollow.objects.filter(user_id=user.id, follow_id=id_).exists():
                        dic['is_follow'] = True
                fan_list.append(dic)
        result = {'result': 1, 'message': "获取粉丝列表成功", "user": user.to_dic() if user else {},
                  "fan_list": fan_list, }
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 获取用户创建收藏夹列表
def get_create_music_list(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        if not MusicList.objects.filter(creator=user).exists():
            result = {'result': 0, 'message': '此用户没有创建歌单'}
            return JsonResponse(result)
        # 外键会自动转成id
        get_music_list = MusicList.objects.filter(creator_id=user_id).all()
        create_music_list = [x.to_dic() for x in get_music_list]
        playlist_num = len(create_music_list)
        result = {'result': 1, 'message': '获取用户创建收藏夹成功', 'create_music_list': create_music_list,
                  'playlist_num': playlist_num}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 获取用户喜爱歌手列表
def get_like_singer_simple(request):
    if request.method == 'GET':
        JWT = request.GET.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        if not User.objects.filter(id=user_id).exists():
            result = {'result': 0, 'message': '不存在该用户'}
            return JsonResponse(result)
        if not UserToSinger.objects.filter(user_id=user_id).exists():
            result = {'result': 0, 'message': '该用户没有喜爱的歌手'}
            return JsonResponse(result)
        singer_id = [x.singer_id for x in UserToSinger.objects.filter(user_id=user_id).all()]
        like_singer_list = [Singer.objects.get(id=y).to_dic_id() for y in singer_id]
        result = {'result': 1, 'message': '获取用户喜爱歌手列表成功', 'like_singer_list': like_singer_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 返回最近播放歌曲列表
def get_recent_listen_music_list(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        history_record = user.history_record
        if not UserListenHistory.objects.filter(user_id=user_id).exists():
            result = {'result': 1, 'message': '此用户目前还没有听歌'}
            return JsonResponse(result)
        history = UserListenHistory.objects.filter(user_id=user_id).all().order_by('-create_date')[:history_record]
        music_list = []
        if history:
            for music in history:
                dic = dict()
                get_music = Music.objects.get(id=music.music_id)
                dic['id'] = get_music.id
                dic['music_name'] = get_music.music_name
                dic['singer_name'] = get_music.singer.name
                music_list.append(dic)
        result = {'result': 1, 'message': '成功获取用户最近播放列表', 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 返回用户最近一周/全部时间内听得最多的十首歌
def get_most_listen_music_list(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        get_type = request.GET.get('op')
        if get_type == '1':
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
        elif get_type == '2':
            # 全部时间内听歌记录
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
            dic = dict()
            get_music = Music.objects.get(id=music['music_id'])
            dic['id'] = get_music.id
            dic['music_name'] = get_music.music_name
            # 增加用户听这首歌的次数
            dic['user_listen_times'] = music['times']
            music_list.append(dic)
        if get_type == 1:
            result = {'result': 1, 'message': '成功获取用户当周听歌历史', 'music_list': music_list}
        else:
            result = {'result': 1, 'message': '成功获取用户当前听歌历史', 'music_list': music_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 喜欢或取消喜欢
def like_or_unlike_music(request):
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
        music_id = request.POST.get('music_id')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        like_list = MusicList.objects.get(id=user.like_list)
        if like_list.music.filter(id=music_id).exists():
            # 取消喜欢
            like_list.music.remove(music)
            music.del_likes()
            like_list.del_music()
            msg = '取消喜欢歌曲成功'
            flag = 1
        else:
            # 喜欢
            like_list.music.add(music)
            music.add_likes()
            like_list.add_music()
            msg = '喜欢歌曲成功'
            flag = 2
        result = {'result': 1, 'message': msg, 'flag': flag}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 喜欢歌曲
def like_music(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id', '')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 注册时创建,一定存在
        like_music_list = MusicList.objects.get(id=user.like_list)
        if like_music_list.music.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲已经在您喜爱的歌曲列表中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        # 歌曲喜欢数加1,喜欢歌单歌曲数加1
        music.add_likes()
        like_music_list.music.add(music)
        like_music_list.add_music()
        like_music_list.save()
        result = {'result': 1, 'message': '已成功添加到喜爱歌曲列表'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 取消喜欢歌曲
def unlike_music(request):
    if request.method == 'POST':
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        like_music_list = MusicList.objects.get(id=user.like_list)
        if not like_music_list.music.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲未在喜欢的歌曲列表中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        # 歌曲喜欢数减1,喜欢歌单歌曲数减1
        music.del_likes()
        like_music_list.music.remove(music)
        like_music_list.del_music()
        like_music_list.save()
        result = {'result': 1, 'message': '已成功取消喜欢此歌曲'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 创建收藏夹
def create_favorites(request):
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
        # 创建收藏夹需要提供名称，不考虑重名
        create_name = request.POST.get('favorites_name', '')
        if len(create_name) == 0:
            result = {'result': 0, 'message': '收藏夹名不能为空'}
            return JsonResponse(result)

        user = User.objects.get(id=user_id)
        description = request.POST.get('description', '')
        new_favorites = MusicList(name=create_name, creator=user, type=1, description=description)
        new_favorites.save()
        # 处理上传封面
        music_list_cover = request.FILES.get('cover')
        bucket = Bucket()
        if music_list_cover:
            if music_list_cover.size > 2 * 1024 * 1024:
                new_favorites.delete()
                result = {'result': 0, 'message': '封面大小不能超过2M'}
                return JsonResponse(result)

            suffix_music_list_cover = '.' + music_list_cover.name.split('.')[-1]
            # 修改封面文件流对象的名称
            music_list_cover.name = 'music_list_cover' + str(new_favorites.id) + suffix_music_list_cover

            # 临时保存到本地
            music_list_cover_dir = os.path.join(MEDIA_ROOT, music_list_cover.name)

            with open(music_list_cover_dir, 'wb+') as destination:
                for chunk in music_list_cover.chunks():
                    destination.write(chunk)
                destination.close()

            # 上传封面
            upload_result = bucket.upload_file('hypermusic', music_list_cover.name, music_list_cover.name)

            if upload_result == -1:
                # 删除歌单
                new_favorites.delete()
                result = {'result': 0, 'message': '上传失败'}
                # 删除本地存储
                os.remove(music_list_cover_dir)
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('hypermusic', music_list_cover.name)

            if audit_dic.get('result') != 0:
                bucket.delete_object('hypermusic', music_list_cover.name)
                new_favorites.delete()
                os.remove(music_list_cover_dir)
                result = {'result': 0, 'message': '歌单封面审核失败'}
                return JsonResponse(result)

            # 获取存储路径
            cover_path = bucket.query_object('hypermusic', music_list_cover.name)
            if not cover_path:
                new_favorites.delete()
                os.remove(music_list_cover_dir)
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            new_favorites.cover_path = cover_path
            new_favorites.save()
            # 删除本地文件
            os.remove(music_list_cover_dir)

        result = {'result': 1, 'message': '收藏夹创建成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 获取用户当前已经创建的收藏夹
def get_favorites(request):
    if request.method == 'GET':
        # 检查表单信息
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        if not MusicList.objects.filter(creator=user, type=1).exists():
            result = {'result': 0, 'message': '当前用户未创建收藏夹'}
            return JsonResponse(result)
        favorites = MusicList.objects.filter(creator=user, type=1).all()
        favorites_list = [x.to_dic() for x in favorites]
        result = {'result': 1, 'message': '获取用户收藏夹成功', 'favorites_list': favorites_list}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 分享歌单
def share_favorites(request):
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
        # 获取要分享的收藏夹
        favorites_id = request.POST.get('favorites_id', '')
        if len(favorites_id) == 0:
            result = {'result': 0, 'message': '请指定要分享的收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=favorites_id, is_public=False).exists():
            result = {'result': 0, 'message': '此收藏夹不存在或已经分享'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=favorites_id, is_public=False)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非歌单创建者,无法分享此歌单'}
            return JsonResponse(result)
        labels = request.POST.getlist('labels', '')
        if len(labels) == 0:
            result = {'result': 0, 'message': '标签不能为空'}
            return JsonResponse(result)

        # # 处理上传歌单封面
        # music_list_cover = request.FILES.get('music_list_front', None)
        # if music_list_cover is None:
        #     # TODO 采用默认封面
        #     pass
        # else:
        #     bucket = Bucket()
        #     # 如果用户上传了封面
        #     suffix_music_list_cover = '.' + music_list_cover.name.split('.')[-1]
        #     music_list_cover.name = 'music_list_cover' + str(favorites_id) + suffix_music_list_cover
        #
        #     # 审核封面
        #     upload_result = bucket.upload_file('hypermusic', music_list_cover.name, music_list_cover.name)
        #     if upload_result == -1:
        #         result = {'result': 0, 'message': '上传失败'}
        #         return JsonResponse(result)
        #     # 获取审核结果
        #     audit_dic = bucket.image_audit('hypermusic',music_list_cover.name)
        #     if audit_dic.get('result') != 0:
        #         bucket.delete_object('hypermusic', music_list_cover.name)
        #         result = {'result': 0, 'message': '歌曲封面审核失败'}
        #         return JsonResponse(result)
        #
        #     # 获取存储路径
        #     music_list_cover_path = bucket.query_object('hypermusic', music_list_cover.name)
        #     if not music_list_cover_path:
        #         result = {'result': 0, 'message': '上传封面失败'}
        #         return JsonResponse(result)
        #     favorites_list.cover_path = music_list_cover_path
        #     favorites_list.save()

        # 标签
        # 已经存在就加入
        for label_name in labels:
            # 判断是否默认标签, 若不是则转为其他
            if label_name not in music_list_labels:
                label_name = '其他'
            if Label.objects.filter(label_name=label_name).exists():
                label = Label.objects.get(label_name=label_name)
                label.label_music_list.add(favorites_list)
                label.save()
            # 不存在就新建标签
            else:
                label = Label(label_name=label_name)
                label.save()
                label.label_music_list.add(favorites_list)
                label.save()
        favorites_list.is_public = True
        favorites_list.save()
        result = {'result': 1, 'message': '歌单分享成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 用户取消分享歌单
def unshare_favorites(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT', '')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        # 获取要取消分享的收藏夹
        favorites_id = request.POST.get('favorites_id', '')
        if len(favorites_id) == 0:
            result = {'result': 0, 'message': '请指定要分享的收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=favorites_id, is_public=True).exists():
            result = {'result': 0, 'message': '此歌单不存在或未分享'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=favorites_id, is_public=True)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非歌单创建者,无法取消分享此歌单'}
            return JsonResponse(result)
        # 删除标签中对应的歌单,仅仅删除关系
        labels = Label.objects.all()
        for label in labels:
            if label.label_music_list.filter(id=favorites_id).exists():
                label.label_music_list.remove(favorites_list)
        # 删除此歌单对应封面
        suffix_music_list_cover = favorites_list.cover_path.split('.')[-1]
        bucket = Bucket()
        bucket.delete_object('hypermusic', 'music_list_cover' + str(favorites_id) + suffix_music_list_cover)
        # 取消分享标志
        favorites_list.is_public = False
        favorites_list.save()
        result = {'result': 1, 'message': '取消分享歌单成功'}
        return JsonResponse(result)
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
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 要收藏的歌曲id
        music_id = request.POST.get('music_id', '')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        list_id = request.POST.get('favorites_id', '')
        if len(list_id) == 0:
            result = {'result': 0, 'message': '请指定收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=list_id)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非收藏夹创建者,无权限操作此收藏夹'}
            return JsonResponse(result)
        if favorites_list.music.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲已在收藏夹中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        favorites_list.music.add(music)
        # 增加歌曲数量
        favorites_list.add_music()
        favorites_list.save()
        result = {'result': 1, 'message': '已成功添加到收藏夹'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 从收藏夹中删除某首歌曲
def unmark_music(request):
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
        # 要取消收藏的歌曲id
        music_id = request.POST.get('music_id')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请指定歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        list_id = request.POST.get('favorites_id', '')
        if len(list_id) == 0:
            result = {'result': 0, 'message': '请指定收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=list_id)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非收藏夹创建者,无权限操作此收藏夹'}
            return JsonResponse(result)
        if not favorites_list.music.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲不在收藏夹中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        favorites_list.music.remove(music)
        favorites_list.del_music()
        favorites_list.save()
        result = {'result': 1, 'message': '已成功从收藏夹移除'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 从他人分享歌单中批量收藏歌曲
def mark_music_list(request):
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
        # 要收藏的歌单id
        music_list_id = request.POST.get('music_list_id', '')
        if len(music_list_id) == 0:
            result = {'result': 0, 'message': '请指定歌单'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=music_list_id, is_public=True).exists():
            result = {'result': 0, 'message': '该歌单不存在或非公开歌单'}
            return JsonResponse(result)
        # 指定的收藏夹
        favorites_list_id = request.POST.get('favorites_id', '')
        if len(music_list_id) == 0:
            result = {'result': 0, 'message': '请指定收藏夹'}
            return JsonResponse(result)
        if music_list_id == favorites_list_id:
            result = {'result': 0, 'message': '收藏夹与要收藏歌单不能相同哦'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=favorites_list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        # 获取指定收藏夹
        favorites_list = MusicList.objects.get(id=favorites_list_id)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非收藏夹创建者,无权限操作此收藏夹'}
            return JsonResponse(result)
        # 获取收藏歌单
        music_list = MusicList.objects.get(id=music_list_id)
        # 遍历收藏指定歌单中的歌曲
        music_s = music_list.music.all()
        for music in music_s:
            # 不存在则收藏
            # TODO 重复收藏是否报错？多对多关系add方法是沉默的
            favorites_list.music.add(music)
            favorites_list.add_music()
        favorites_list.save()
        result = {'result': 1, 'message': '已成功收藏歌单'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误！"}
        return JsonResponse(result)


# 设置记录的最近播放数量
def set_history_record(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        history_record = request.POST.get('history_record', None)
        if history_record is None:
            result = {'result': 0, 'message': '最大数量不能为空'}
            return JsonResponse(result)
        if history_record not in ['10', '20', '50']:
            result = {'result': 0, 'message': '最大数量只能为10/20/50'}
            return JsonResponse(result)
        user.history_record = history_record
        user.save()
        result = {'result': 1, 'message': '最大记录数量设置成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 播放音乐
def play_music(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        user = None
        if JWT != '-1':
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        music_id = request.POST.get('music_id', '')
        if len(music_id) == 0:
            result = {'result': 0, 'message': '请选择要播放的歌曲'}
            return JsonResponse(result)
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        music.add_listen_times()
        # 若为登录用户,需要添加播放记录
        if user:
            history = UserListenHistory(user_id=user_id,music_id=music_id)
            history.save()
        result = {'result': 1, 'message': '成功播放歌曲'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)



# 用户删除其创建的收藏夹
def del_favorites(request):
    if request.method == 'POST':
        # 检查表单信息
        JWT = request.POST.get('JWT')
        user = None
        if JWT != '-1':
            try:
                token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
                user_id = token.get('user_id', '')
                user = User.objects.get(id=user_id)
            except Exception as e:
                result = {'result': 0, 'message': "请先登录"}
                return JsonResponse(result)
        # 获取要删除的收藏夹
        favorites_id = request.POST.get('favorites_id', '')
        if favorites_id == '':
            result = {'result': 0, 'message': '请指定要删除的收藏夹'}
            return JsonResponse(result)
        if not MusicList.objects.filter(id=favorites_id, creator=user).exists():
            result = {'result': 0, 'message': '不存在此收藏夹或没有权限'}
            return JsonResponse(result)
        favorites = MusicList.objects.get(id=favorites_id)
        favorites.delete()
        result = {'result': 1, 'message': '删除收藏夹成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)