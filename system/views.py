from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
from django.db.models import F

from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from datetime import datetime, timedelta
from hashlib import md5
import smtplib
import uuid
import base64

from system.models import User, Role, UserRole, Module, Permission


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


# 登录
@require_POST
def login_user(request):
    # try:
    #     del request.session['username_session']
    #     del request.session['user_permission']
    # except Exception as e:
    #     pass

    try:
        username = request.POST.get('username')
        pd = request.POST.get('password')
        remember = request.POST.get('remember')

        password = md5(pd.encode(encoding='utf-8')).hexdigest()

        user = User.objects.get(username=username, password=password)

        username_session = request.session.get('username_session')
        # 如果用户存在，存储session信息
        if not username_session:
            request.session['username_session'] = username

            # 设置失效时间,关闭浏览器失效
            request.session.set_expiry(0)

        # 如果用户存在，则根据用户查角色权限
        # roleId = UserRole.objects.values_list('role_id', flat=True).filter(user_id=user.id)
        # roleId = user.roles.values_list('id', flat=True).all()
        # user_permission = Permission.objects.filter(role_id__in=list(roleId)).values_list('module__optValue')
        # permission_session = request.session.get('user_permission')
        # if permission_session is None:
        #     request.session['user_permission'] = list(user_permission)
        #     request.session.set_expiry(0)
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
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        old_pd = md5(old_password.encode(encoding='utf-8')).hexdigest()
        user = User.objects.get(username=username, password=old_pd)

        new_pd = md5(new_password.encode(encoding='utf-8')).hexdigest()
        user.password = new_pd
        user.save()

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


@require_GET
def select_customer_manager(request):
    try:
        # ones = Role.objects.values('id').filter(roleName__exact='客户经理')
        # id = list(ones)[0]['id']
        names = UserRole.objects.annotate(username=F('user__username')).values('username').filter(
            role__roleName__exact='客户经理')
        # Role.objects.values('username').filter(userrole=id)
        return JsonResponse(list(names), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


def module_index(request):
    return render(request, 'system/module.html')


@require_GET
def select_module(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        ones = Module.objects.values().order_by('grade')
        # {'模型属性名': 'select DATE_FORMAT(数据库列名, '格式化样式')'}
        # select = {'createDate': "select DATE_FORMAT(create_date, '%%Y-%%m-%%d %%H:%%i:%%s')",
        #           'updateDate': "select DATE_FORMAT(update_date, '%%Y-%%m-%%d %%H:%%i:%%s')"}
        # ones = Module.objects.extra(select=select).values('id', 'moduleName', 'moduleStyle',
        #                                                   'url', 'optValue', 'grade', 'orders', 'parent',
        #                                                   'createDate', 'updateDate').order_by('grade')
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@require_GET
def select_module_by_grade(request):
    try:
        grade = request.GET.get('grade')
        ones = Module.objects.values('id', 'moduleName').filter(grade=grade)
        return JsonResponse(list(ones), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


def opt_value_has(optValue):
    flag = Module.objects.filter(optValue=optValue)
    return flag


@csrf_exempt
@require_POST
def update_module(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        parent = data.pop('parent')
        temp_module = Module.objects.get(pk=id)
        if temp_module.optValue != data.get('optValue'):
            if opt_value_has(request.POST.get('optValue')):
                return JsonResponse({'code': 400, 'msg': '操作权限重复'})
        if parent:
            p = Module.objects.get(pk=parent)
            data['parent'] = p
        data['updateDate'] = datetime.now()
        Module.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@csrf_exempt
@require_POST
def create_module(request):
    try:
        data = request.POST.dict()
        data.pop('id')
        parent = data.pop('parent')
        if opt_value_has(request.POST.get('optValue')):
            return JsonResponse({'code': 400, 'msg': '操作权限重复'})
        if parent:
            p = Module.objects.get(pk=parent)
            data['parent'] = p
        Module.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


@require_GET
def delete_module(request):
    try:
        ids = request.GET.get('ids')
        ids = ids.split(',')
        Module.objects.filter(id__in=ids).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


def role_index(request):
    return render(request, 'system/role.html')


@require_GET
def select_role(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        ones = Role.objects.values().order_by('-id')
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def create_role(request):
    try:
        data = request.POST.dict()
        data.pop('id')
        Role.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


@csrf_exempt
@require_POST
def update_role(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        Role.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@require_GET
def delete_role(request):
    try:
        ids = request.GET.get('ids')
        ids = ids.split(',')
        Role.objects.filter(id__in=ids).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@require_GET
def role_module_index(request):
    try:
        id = request.GET.get('id')
        # 查询角色
        one = Role.objects.get(pk=id)
        # 查询模块
        module = list(Module.objects.values('id', 'parent', 'moduleName').all())
        # 查询角色所拥有的模块
        role_module = Permission.objects.values_list('module', flat=True).filter(role_id=id).all()
        for m in module:
            if m.get('id') in role_module:
                m['checked'] = 'true'
            else:
                m['checked'] = 'false'
        return render(request, 'system/role_module.html', {'role': one, 'module': module})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def role_relate_module(request):
    try:
        return JsonResponse({'code': 200, 'msg': '绑定成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '绑定失败'})


@csrf_exempt
@require_POST
def role_relate_module(request):
    try:
        module_ids = request.POST.get('module_checked_id')
        role_id = request.POST.get('role_id')

        # 刪除所有角色權限
        Permission.objects.filter(role__id=role_id).delete()

        if not module_ids:
            return JsonResponse({'code': 200, 'msg': '操作成功'})

        role = Role.objects.get(pk=role_id)
        modules = Module.objects.filter(id__in=module_ids.split(',')).all()
        data_to_in = []
        for m in modules:
            data_to_in.append(Permission(role=role, module=m))
        Permission.objects.bulk_create(data_to_in)
        return JsonResponse({'code': 200, 'msg': '操作成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '操作失败'})


def user_index(request):
    return render(request, 'system/user.html')


@require_GET
def select_user(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        ones = User.objects.values().order_by('-id')
        name = request.GET.get('name')
        if name:
            ones = ones.filter(username__contains=name)
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@require_GET
def select_role_for_user(request):
    try:
        ones = Role.objects.values()
        return JsonResponse(list(ones), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def create_user(request):
    try:
        data = request.POST.dict()
        username = data.get('username')
        one = User.objects.filter(username=username)
        if one:
            return JsonResponse({'code': 400, 'msg': '用户名已经存在'})
        email = data.get('email')
        one = User.objects.filter(email=email)
        if one:
            return JsonResponse({'code': 400, 'msg': '邮箱已经存在'})
        # role_ids = data.pop('roles_hidden')
        role_ids = request.POST.getlist('roles')
        data.pop('id')
        data.pop('roles')
        # 使用md5加密
        data['password'] = md5(data.get('password').encode(encoding='utf-8')).hexdigest()
        one = User.objects.create(**data)
        roles = Role.objects.filter(id__in=role_ids).all()
        data_to_in = []
        for role in roles:
            data_to_in.append(UserRole(user=one, role=role))
        UserRole.objects.bulk_create(data_to_in)
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


@require_GET
def select_role_by_userid(request):
    try:
        id = request.GET.get('id')
        ones = UserRole.objects.values_list('role', flat=True).filter(user_id=id)
        return JsonResponse(list(ones), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def update_user(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        tempOne = User.objects.get(pk=id)
        username = data.get('username')
        if username != tempOne.username:
            one = User.objects.filter(username=username)
            if one:
                return JsonResponse({'code': 400, 'msg': '用户名已经存在'})
        email = data.get('email')
        if email != tempOne.email:
            one = User.objects.filter(email=email)
            if one:
                return JsonResponse({'code': 400, 'msg': '邮箱已经存在'})
        # role_ids = data.pop('roles_hidden')
        role_ids = request.POST.getlist('roles')
        data.pop('roles')
        # 使用md5加密
        data['password'] = md5(data.get('password').encode(encoding='utf-8')).hexdigest()
        data['update_date'] = datetime.now()
        User.objects.filter(pk=id).update(**data)
        roles = Role.objects.filter(id__in=role_ids).all()
        UserRole.objects.filter(user_id=id).delete()
        data_to_in = []
        for role in roles:
            data_to_in.append(UserRole(user=tempOne, role=role))
        UserRole.objects.bulk_create(data_to_in)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@require_GET
def delete_user(request):
    try:
        ids = request.GET.get('ids')
        User.objects.filter(id__in=ids.split(',')).update(isValid=0, update_date=datetime.now())
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})
