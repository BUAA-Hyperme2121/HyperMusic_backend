from django.shortcuts import render
from user.models import User
from django.http import JsonResponse
# Create your views here.
import hashlib

def check_password(password):
    if not str.isalnum(password):
        return False
    if len(password) < 8 or len(password) > 18:
        return False
    return True


def trans_password(password):
    transed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    transed_password = str(transed_password)
    return transed_password


  # 跨域设置
def register(request):  # 继承请求类
    if request.method == 'POST':  # 判断请求方式是否为 POST（要求POST方式）
        username = request.POST.get('username')  # 获取请求数据
        password_1 = request.POST.get('password_1')
        password_2 = request.POST.get('password_2')

        username_check = User.objects.filter(username=username)
        if password_1 != password_2:  # 若两次输入的密码不同，则返回错误码errno和描述信息msg
            return JsonResponse({'errno': 1002, 'msg': "两次输入的密码不同"})
        elif not str.isalnum(username):
            return JsonResponse({'errno': 1003, 'msg': "用户名不合法"})
        elif username_check.exists():
            return JsonResponse({'errno': 1004, 'msg': "用户已存在"})
        elif not check_password(password=password_1):
            return JsonResponse({'errno':1005, 'msg':'密码不合法'})
        else:
            # 数据库存取：新建 Author 对象，赋值用户名和密码并保存
            new_author = User(username=username, password=trans_password(password_1))
            new_author.save()  # 一定要save才能保存到数据库中
            return JsonResponse({'errno': 0, 'msg': "注册成功"})
    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # 获取请求数据
        password = request.POST.get('password')
        author = User.objects.filter(username=username)
        if not author.exists():  # 判断用户名是否存在
            return JsonResponse({'errno': 1003, 'msg': "用户名不存在"})
        author = author[0]
        password = trans_password(password)

        if author.password == password:  # 判断请求的密码是否与数据库存储的密码相同
            request.session['username'] = username  # 密码正确则将用户名存储于session（django用于存储登录信息的数据库位置）
            return JsonResponse({'errno': 0, 'msg': "登录成功"})
        else:
            return JsonResponse({'errno': 1002, 'msg': "账号或密码错误"})
    else:
        return JsonResponse({'errno': 1001, 'msg': "请求方式错误"})