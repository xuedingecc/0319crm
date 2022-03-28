from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from datetime import datetime, timedelta
from hashlib import md5
import smtplib
import uuid
import base64

from system.models import User


def login_register(request):
    return render(request, 'login_register.html')


@require_POST
def unique_username(request):
    try:
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        return JsonResponse({'code': 400, 'msg': '该用户已存在'})
    except User.DoesNotExist:
        return JsonResponse({'code': 200, 'msg': '恭喜你，用户名可以注册'})


@require_POST
def unique_email(request):
    try:
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        return JsonResponse({'code': 400, 'msg': '该邮箱已注册'})
    except User.DoesNotExist:
        return JsonResponse({'code': 200, 'msg': '恭喜你，邮箱可以注册'})


def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode('utf-8'), addr))


@require_POST
def send_email(request):
    try:
        from_addr = '17625212308@163.com'
        # 邮箱授权码
        from_pwd = 'NVWHTBVDDPRDAFCN'
        smtp_server = 'smtp.163.com'
        to_addr = request.POST.get('email')

        # 激活码
        code = ''.join(str(uuid.uuid4()).split('-'))
        # 10min后的时间戳
        tt = datetime.now() + timedelta(minutes=10)
        ts = str(tt.timestamp()).split('.')[0]

        to_name = request.POST.get('username')
        pd = request.POST.get('password')
        # 使用md5加密
        password = md5(pd.encode(encoding='utf-8')).hexdigest()

        html = """
            <html>
                <body>
                    <a href='http://127.0.0.1:8000/system/active_account/?username={}&code={}&timestamp={}'>点击注册</a>
                </body>
            </html>
        """.format(to_name, code, ts)
        msg = MIMEText(html, 'html', 'utf-8')

        msg['From'] = format_addr(f'诚本地<{from_addr}>')
        msg['To'] = format_addr(f'{to_name}<{to_addr}>')
        msg['Subject'] = Header(u'本地CRM', 'utf-8').encode()

        with transaction.atomic():
            user = User.objects.create(username=to_name, password=password, email=to_addr, code=code, timestamp=ts)
            user.save()
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, from_pwd)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()
            return JsonResponse({'code': 200, 'msg': '注册成功，请前往邮箱激活账号'})
    except smtplib.SMTPException as e:
        return JsonResponse({'code': 400, 'msg': '注册失败，请重新注册'})


@require_GET
def active_account(request):
    try:
        username = request.GET.get('username')
        code = request.GET.get('code')
        timestamp = request.GET.get('timestamp')

        user = User.objects.get(username=username, code=code, timestamp=timestamp)

        if int(str(datetime.now().timestamp()).split('.')[0]) < int(timestamp):
            user.code = ''
            user.status = 1  # 有效账号
            user.save()
            return HttpResponse('<h1>激活成功，请<a href="http://127.0.0.1:8000/system/login_register/">前往登录</a></h1>')
        else:
            user.delete()
            # return JsonResponse({'ret': 400, 'msg': '链接失效，请重新注册'})
            return HttpResponse('<h1>链接失效，请<a href="http://127.0.0.1:8000/system/login_register/">重新注册</a></h1>')
    except Exception as e:
        if isinstance(User.DoesNotExist, e):
            return HttpResponse('<h1>激活失败，请<a href="http://127.0.0.1:8000/system/login_register/">重新注册</a></h1>')
        return HttpResponse('网络波动，激活失败，请<a href="http://127.0.0.1:8000/system/login_register/">重新注册</a></h1>')


@require_POST
def login_user(request):
    try:
        username = request.POST.get('username')
        pd = request.POST.get('password')
        remember = request.POST.get('remember')

        password = md5(pd.encode(encoding='utf-8')).hexdigest()

        user = User.objects.get(username=username, password=password)

        # 如果用户存在，存储session信息
        request.session['username_session'] = username

        # 设置失效时间,关闭浏览器失效
        request.session.set_expiry(0)

        context = {
            'code': 200,
            'msg': '欢迎回来'
        }

        # 如果用户存在，前台js存储cookie
        if remember == 'true':
            context['login_cookie'] = base64.b64encode((username + '&' + pd).encode(encoding='utf-8')).decode(
                encoding='utf-8')

        return JsonResponse(context)
    except User.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '用户名或密码错误'})


# 跳转首页
def index(request):
    # 判断session中是否有用户信息
    username = request.session.get('username_session')

    if username:
        return render(request, 'system/index.html')
    return redirect('system:login_register')


# 修改密码
@require_POST
def update_password(request):
    try:
        # username = request.POST.get('username')
        # old_password = request.POST.get('old_password')
        # new_password = request.POST.get('new_password')
        #
        # old_pd = md5(old_password.encode(encoding='utf-8')).hexdigest()
        # user = User.objects.get(username=username, password=old_pd)
        #
        # new_pd = md5(new_password.encode(encoding='utf-8')).hexdigest()
        # user.password = new_pd
        # user.save()

        return JsonResponse({'code': 200, 'msg': '修改成功'})
    except User.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '原密码输入错误'})


# 安全退出
def logout(request):
    try:
        # 清除session
        request.session.flush()
        return redirect('system:login_register')
    except Exception as e:
        return redirect('system:login_register')
