# Create your views here.
import hashlib
from datetime import *
from random import Random

import jwt
from django.db.models import Count
from django.http import JsonResponse

from Bucket import *
from Message.views import verify_code
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


def create_code(random_length=6):
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
        user.like_list = like_list
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
            avatar.name = str(user.id) + suffix

            bucket = Bucket()
            key = create_code()

            # 上传审核
            upload_result = bucket.upload_file('avatar', key + suffix, avatar.name)
            if upload_result == -1:
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('avatar', key + suffix)
            if audit_dic.get('result') != 0:
                bucket.delete_object('avatar', key + suffix)
                result = {'result': 0, 'message': '审核不通过', 'user': user.to_dic()}
                return JsonResponse(result)
            # 删除用于审核的对象
            bucket.delete_object('avatar', key + suffix)

            # TODO 判断是否默认头像，若不是，删除以前存储的，否则存储名重复

            # 审核通过,正式上传
            upload_result = bucket.upload_file('avatar', str(user_id) + suffix, avatar.name)
            if upload_result == -1:
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            # 获取存储路径
            avatar_path = bucket.query_object('avatar', str(user_id) + suffix)
            if not avatar_path:
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            user.avatar_path = avatar_path
            user.save()

        location = request.POST.get('location', '')
        gender = request.POST.get('gender', '')
        introduction = request.POST.get('introduction', '这个人很懒，什么都没有留下')
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

        labels_music = request.POST.get('music_labels', '')
        labels_singer = request.POST.get('singer_labels', '')
        music_name = request.POST.get('music_name', '')
        music_cover = request.FILES.get('music_cover', None)
        description = request.POST.get('description', '')
        singer_name = request.POST.get('singer_name', '')
        singer_cover = request.FILES.get('singer_cover', None)
        lyrics = request.FILES.get('lyrics', None)

        if music_name == '' or labels_music == '' or singer_name == '':
            result = {'result': 0, 'message': '歌曲名称或歌曲标签或创作歌手不能为空'}
            return JsonResponse(result)

        if len(music_name) > 100:
            result = {'result': 0, 'message': '歌曲名过长'}
            return JsonResponse(result)
        # 歌曲重名
        if Music.objects.filter(singer_name=singer_name, music_name=music_name).exists():
            result = {'result': 0, 'message': '歌曲已存在'}
            return JsonResponse(result)
        # 音源文件不存在
        music_upload = request.FILES.get('music', None)
        if not music_upload:
            result = {'result': 0, 'message': '上传歌曲不能为空'}
            return JsonResponse(result)

        music = Music(music_name=music_name, description=description, creator=user)
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
            suffix_music_cover = '.' + music_cover.name.split('.')[-1]
            music_cover.name = str(music_id) + suffix_music_cover

            # 审核封面
            key = create_code()
            upload_result = bucket.upload_file('music_cover', key + suffix_music_cover, music_cover.name)
            if upload_result == -1:
                # 删除歌曲对象
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('music_cover', key + suffix_music_cover)
            if audit_dic.get('result') != 0:
                bucket.delete_object('music_cover', key + suffix_music_cover)
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '歌曲封面审核失败'}
                return JsonResponse(result)
            # 审核通过则删除审核对象
            bucket.delete_object('music_cover', key + suffix_music_cover)

            # 正式上传封面
            upload_result = bucket.upload_file('music_cover', str(music_id) + suffix_music_cover, music_cover.name)
            if upload_result == -1:
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            # 获取存储路径
            music_cover_path = bucket.query_object('music_cover', str(music_id) + suffix_music_cover)
            if not music_cover_path:
                Music.objects.get(id=music_id).delete()
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            music.cover_path = music_cover_path
            music.save()

        # 上传歌曲
        if music_upload.size > 1024 * 1024 * 20:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
            Music.objects.get(id=music_id).delete()
            result = {'result': 0, 'message': '音频大小不能超过20M'}
            return JsonResponse(result)

        suffix_music = '.' + music_upload.name.split('.')[-1]
        music_upload.name = str(music_id) + suffix_music
        upload_result = bucket.upload_file('music', str(music_id) + suffix_music, music_upload.name)
        if upload_result == -1:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
            Music.objects.get(id=music_id).delete()
            result = {'result': 0, 'message': '上传歌曲失败'}
            return JsonResponse(result)
        # 上传是否可以获得路径
        music_path = bucket.query_object('music', str(music_id) + suffix_music)
        if not music_path:
            if music.cover_path != '':
                bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
            Music.objects.get(id=music_id).delete()
            result = {'result': 0, 'message': '上传歌曲失败'}
            return JsonResponse(result)

        # 获取桶存储路径成功
        music.music_path = music_path
        music.save()

        audit_dic = bucket.music_audit_submit('music', str(music_id) + suffix_music)
        if audit_dic.get('result', 0) == -1 or audit_dic.get('result', 0) == 0:
            if music.cover_path != '':
                # 删除封面
                bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
            bucket.delete_object('music', str(music_id) + suffix_music)
            Music.objects.get(id=music_id).delete()
            result = {'result': 0, 'message': '上传歌曲失败'}
            return JsonResponse(result)

        # 设置歌手,有就记录,无就新建
        if Singer.objects.filter(name=singer_name).exists():
            singer_to_music = SingerToMusic(singer_name=singer_name, music_name=music_name)
            singer_to_music.save()
        else:
            singer = Singer(name=singer_name)
            singer.save()
        singer = Singer.objects.get(name=singer_name)
        singer_id = singer.id

        suffix_singer_cover = ''
        # 处理歌手封面
        if singer_cover:
            suffix_singer_cover = '.' + singer_cover.name.split('.')[-1]
            singer_cover.name = str(singer_id) + suffix_singer_cover

            # 审核封面
            key = create_code()
            upload_result = bucket.upload_file('singer_cover', key + suffix_singer_cover, singer_cover.name)
            if upload_result == -1:
                # 删除桶存储歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(id=singer_id).delete()
                result = {'result': 0, 'message': '上传歌手封面失败'}
                return JsonResponse(result)

            # 获取审核结果
            audit_dic = bucket.image_audit('singer_cover', key + suffix_singer_cover)
            if audit_dic.get('result') != 0:
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除审核对象
                bucket.delete_object('singer_cover', key + suffix_singer_cover)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(id=singer_id).delete()
                result = {'result': 0, 'message': '歌手封面审核失败'}
                return JsonResponse(result)
            # 审核通过则删除审核对象
            bucket.delete_object('singer_cover', key + suffix_singer_cover)

            # 正式上传封面
            upload_result = bucket.upload_file('singer_cover', str(singer_id) + suffix_singer_cover, singer_cover.name)
            if upload_result == -1:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(name=singer_name).delete()
                result = {'result': 0, 'message': '上传歌手封面失败'}
                return JsonResponse(result)
            # 获取存储路径
            cover_path = bucket.query_object('singer_cover', str(singer_id) + suffix_singer_cover)
            if not cover_path:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(name=singer_name).delete()
                result = {'result': 0, 'message': '上传歌手封面失败'}
                return JsonResponse(result)
            singer.cover_path = cover_path
            singer.save()
        # TODO 设置歌手默认封面,歌曲默认封面

        # 处理用户上传歌词
        if lyrics:
            suffix_lyrics = '.' + lyrics.name.split('.')[-1]
            lyrics.name = str(music_id) + suffix_lyrics
            upload_result = bucket.upload_file('lyrics', str(music_id) + suffix_lyrics, lyrics.name)
            if upload_result == -1:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除歌手封面
                if singer.cover_path != '':
                    bucket.delete_object('singer_cover', str(singer_id) + suffix_singer_cover)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(name=singer_name).delete()
                result = {'result': 0, 'message': '上传歌词失败'}
                return JsonResponse(result)

            # 是否可以获取路径
            lyrics_path = bucket.query_object('lyrics', str(music_id) + suffix_lyrics)
            if not lyrics_path:
                # 删除桶存储的歌曲，歌曲封面对象
                if music.cover_path != '':
                    bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
                bucket.delete_object('music', str(music_id) + suffix_music)
                # 删除歌手封面
                if singer.cover_path != '':
                    bucket.delete_object('singer_cover', str(singer_id) + suffix_singer_cover)
                # 删除歌曲,歌手对象
                Music.objects.get(id=music_id).delete()
                Singer.object.get(name=singer_name).delete()
                result = {'result': 0, 'message': '上传歌词失败'}
                return JsonResponse(result)
            music.lyrics_path = lyrics_path
            music.save()

        # 判断是否原创歌曲
        if user.username == singer_name:
            music.is_original = True
            music.save()

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
                label.label_music.add(music)
                label.save()

        # 歌手标签
        if labels_singer != '':
            for label_name in labels_singer:
                if label_name not in singer_labels:
                    label_name = '其他歌手或乐队'
                if Label.objects.filter(label_name=label_name).exists():
                    label = Label.objects.get(label_name=label_name)
                    label.label_singer.add(singer)
                    label.save()
                # 不存在就新建标签
                else:
                    label = Label(label_name=label_name)
                    label.label_singer.add(singer)
                    label.save()
        # 歌手不一定有标签,贴上其他
        label_name = '其他歌手或乐队'
        if Label.objects.filter(label_name=label_name).exists():
            label = Label.objects.get(label_name=label_name)
            label.label_singer.add(singer)
            label.save()
        # 不存在就新建标签
        else:
            label = Label(label_name=label_name)
            label.label_singer.add(singer)
            label.save()

        result = {'result': 1, 'message': '上传歌曲成功'}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': '请求方式错误'}
        return JsonResponse(result)


# 用户删除自己上传歌曲
def del_music(request):
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
        bucket.delete_object('music_cover', str(music_id) + suffix_music_cover)
        if music.lyrics_path != '':
            # 删除歌词
            suffix_lyrics = '.' + music.lyrics_path.split('.')[-1]
            bucket.delete_object('lyrics', str(music_id) + suffix_lyrics)
        # 删除音源
        suffix_music = '.' + music.music_path.split('.')[-1]
        bucket.delete_object('music', str(music_id) + suffix_music)
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
        if JWT != "-1":
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
        for id in follow_list_get:
            dic = User.objects.get(id=id)
            dic['is_follow'] = False
            # 当前用户为登录用户
            if user:
                if UserToFollow.objects.filter(user_id=user.id, follow_id=id).exists():
                    dic['is_follow'] = True
            follow_list.append(dic)
        result = {'result': 1, 'message': "获取粉丝列表成功", "user": user.to_dic(),
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
        for id_ in fan_list_get:
            dic = User.objects.get(id=id_)
            dic['is_follow'] = False
            # 当前用户为登录用户
            if user:
                if UserToFollow.objects.filter(user_id=user.id, follow_id=id_).exists():
                    dic['is_follow'] = True
            fan_list.append(dic)
        result = {'result': 1, 'message': "获取粉丝列表成功", "user": user.to_dic(),
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
        if not MusicList.objects.filter(creator_id=user_id).exists():
            result = {'result': 0, 'message': '此用户没有创建歌单'}
            return JsonResponse(result)
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
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        history_record = user.history_record
        if not UserListenHistory.objects.filter(user_id=user_id).exists():
            result = {'result': 1, 'message': '此用户目前还没有听歌'}
            return JsonResponse(result)
        history = UserListenHistory.objects.filter(user_id=user_id).all().order_by('-create_date')[:history_record]
        music_list = []
        for music in history:
            dic = dict()
            get_music = Music.objects.get(id=music.id)
            dic['id'] = get_music.id
            dic['music_name'] = get_music.music_name
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
        JWT = request.GET.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        get_type = request.GET.get('op')
        if get_type == 1:
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
        elif get_type == 2:
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
            get_music = Music.objects.get(id=music.id)
            dic['id'] = get_music.id
            dic['music_name'] = get_music.music_name
            # 增加用户听这首歌的次数
            dic['user_listen_times'] = music.times
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        like_list = user.like_list
        if like_list.music.filter(id=music_id).exists():
            # 取消喜欢
            like_list.music.remove(music)
            music.del_likes()
            msg = '取消喜欢歌曲成功'
            flag = 1
        else:
            # 喜欢
            like_list.music.add(music)
            music.add_likes()
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
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
        # 歌曲喜欢数加1
        music.add_likes()
        like_music_list.music.add(music)
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
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        user = User.objects.filter(id=user_id)
        like_music_list = MusicList.objects.get(creator=user, type=2)
        if not like_music_list.music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲未在喜欢的歌曲列表中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        # 歌曲喜欢数减1
        music.del_likes()
        like_music_list.music.remove(music)
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 创建收藏夹需要提供名称 TODO 考虑重名？
        flag = False
        create_name = request.POST.get('create_name')
        music_list_all = UserToMusicList.objects.filter(user_id=user_id, type=1).all()
        for ml in music_list_all:
            get_music_list = MusicList.objects.get(id=ml.music_list_id)
            if get_music_list.name == create_name:
                flag = True
                break
        if flag:
            result = {'result': 0, 'message': '你已经创建过同名收藏夹'}
            return JsonResponse(result)
        user = User.objects.get(id=user_id)
        description = request.POST.get('description', '')
        new_favorites = MusicList(name=create_name, creator=user, type=1, description=description)
        new_favorites.save()
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
        user = User.objects.get(id=user_id)
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 获取要分享的收藏夹
        favorites_id = request.POST.get('favorites_id')
        if not MusicList.objects.filter(id=favorites_id, is_share=False).exists():
            result = {'result': 0, 'message': '此收藏夹不存在或已经分享'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=favorites_id, is_share=False)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非歌单创建者,无法分享此歌单'}
            return JsonResponse(result)
        labels = request.POST.get('labels', None)
        if labels is None:
            result = {'result': 0, 'message': '标签不能为空'}
            return JsonResponse(result)

        # 处理上传歌单封面
        music_list_cover = request.FILES.get('music_list_front', None)
        if music_list_cover is None:
            # TODO 采用默认封面
            pass
        else:
            bucket = Bucket()
            # 如果用户上传了封面
            suffix_music_list_cover = '.' + music_list_cover.name.split('.')[-1]
            music_list_cover.name = str(favorites_id) + suffix_music_list_cover

            # 审核封面
            key = create_code()
            upload_result = bucket.upload_file('music_list_cover', key + suffix_music_list_cover, music_list_cover.name)
            if upload_result == -1:
                result = {'result': 0, 'message': '上传失败'}
                return JsonResponse(result)
            # 获取审核结果
            audit_dic = bucket.image_audit('music_list_cover', key + suffix_music_list_cover)
            if audit_dic.get('result') != 0:
                bucket.delete_object('music_list_cover', key + suffix_music_list_cover)
                result = {'result': 0, 'message': '歌曲封面审核失败'}
                return JsonResponse(result)
            # 审核通过则删除审核对象
            bucket.delete_object('music_list_cover', key + suffix_music_list_cover)

            # 正式上传封面
            upload_result = bucket.upload_file('music_list_cover', str(favorites_id) + suffix_music_list_cover,
                                               music_list_cover.name)
            if upload_result == -1:
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            # 获取存储路径
            music_list_cover_path = bucket.query_object('music_list_cover', str(favorites_id) + suffix_music_list_cover)
            if not music_list_cover_path:
                result = {'result': 0, 'message': '上传封面失败'}
                return JsonResponse(result)
            favorites_list.cover_path = music_list_cover_path
            favorites_list.save()

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
                label.label_music_list.add(favorites_list)
                label.save()
        favorites_list.is_share = True
        favorites_list.save()
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)


# 用户取消分享歌单
def unshare_favorites(request):
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
        # 获取要取消分享的收藏夹
        favorites_id = request.POST.get('favorites_id')
        if not Music.objects.filter(id=favorites_id, is_share=True).exists():
            result = {'result': 0, 'message': '此歌单不存在或未分享'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=favorites_id, is_share=True)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非歌单创建者,无法取消分享此歌单'}
            return JsonResponse(result)
        # 删除标签中对应的歌单,仅仅删除关系
        labels = Label.objects.all()
        for label in labels:
            if label.label_music_list.filter(id=favorites_id).exists():
                label.label_music_list.remove(favorites_list)
        # 取消分享标志
        favorites_list.is_share = False
        # 删除此歌单对应封面
        suffix_music_list_cover = favorites_list.cover_path.split('.')[-1]
        bucket = Bucket()
        bucket.delete_object('music_list_cover', str(favorites_id) + suffix_music_list_cover)
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
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        list_id = request.POST.get('favorites_id')
        if not MusicList.objects.filter(id=list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=list_id)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非收藏夹创建者,无权限操作此收藏夹'}
            return JsonResponse(result)
        if favorites_list.music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲已在收藏夹中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        favorites_list.music.add(music)
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 要取消收藏的歌曲id
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '该歌曲不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        list_id = request.POST.get('favorites_id')
        if not MusicList.objects.filter(id=list_id).exists():
            result = {'result': 0, 'message': '不存在对应收藏夹'}
            return JsonResponse(result)
        favorites_list = MusicList.objects.get(id=list_id)
        if favorites_list.creator != user:
            result = {'result': 0, 'message': '抱歉,您非收藏夹创建者,无权限操作此收藏夹'}
            return JsonResponse(result)
        if not favorites_list.music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '此歌曲不在收藏夹中'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        favorites_list.music.remove(music)
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
        JWT = request.POST.get('JWT')
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录!"}
            return JsonResponse(result)
        # 要收藏的歌单id
        music_list_id = request.POST.get('music_list_id')
        if not MusicList.objects.filter(id=music_list_id, is_share=True).exists():
            result = {'result': 0, 'message': '该歌单不存在'}
            return JsonResponse(result)
        # 指定的收藏夹
        favorites_list_id = request.POST.get('favorites_list_id')
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
        music_s = music_list.music.objects.all()
        for music in music_s:
            # 不存在则收藏
            # TODO 重复收藏是否报错？多对多关系add方法是沉默的
            favorites_list.music.add(music)
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
        if history_record != 10 and history_record != 20 and history_record != 50:
            result = {'result': 0, 'message': '最大数量只能为10/20/50'}
            return JsonResponse(result)
        user.history_record = history_record
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
        try:
            token = jwt.decode(JWT, 'secret', algorithms=['HS256'])
            user_id = token.get('user_id', '')
            user = User.objects.get(id=user_id)
        except Exception as e:
            result = {'result': 0, 'message': "请先登录"}
            return JsonResponse(result)
        music_id = request.POST.get('music_id')
        if not Music.objects.filter(id=music_id).exists():
            result = {'result': 0, 'message': '歌曲不存在'}
            return JsonResponse(result)
        music = Music.objects.get(id=music_id)
        music.add_listen_times()
    else:
        result = {'result': 0, 'message': "请求方式错误"}
        return JsonResponse(result)
