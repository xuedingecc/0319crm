from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.deprecation import MiddlewareMixin

from system.models import User, Permission


class CustomSystemException(Exception):
    def __init__(self, code=400, msg='系统异常，请联系管理员'):
        self.code = code
        self.msg = msg

    @staticmethod
    def errormsg(msg):
        c = CustomSystemException(msg)
        return c


class CrmExceptionMiddleware(MiddlewareMixin):
    """全局异常处理中间件"""

    def process_exception(self, request, exception):
        if isinstance(exception, CustomSystemException):
            result = {'code': exception.code, 'msg': exception.msg}
        elif isinstance(exception, Exception) or isinstance(exception, BaseException):
            result = {'code': 400, 'msg': '系统报错'}

        if request.is_ajax():
            return JsonResponse(result)
        else:
            # return JsonResponse(result)
            return render(request, 'error.html', result)


class CrmUrlMiddleware(MiddlewareMixin):
    """全局url拦截中间件"""

    def process_request(self, request):
        # 判断是否是允许访问地址
        urls = ['login_register', 'unique_username', 'unique_email', 'send_email', 'active_accounts']
        url = request.path.split('/')[-2]
        if url not in urls:
            # 如果访问路径不存在，判断session中是否有用户信息，有则放行
            ut = request.POST.get('username')
            username = request.session.get('username_session')
            if not username:
                return redirect('system:login_register')
            if ut and ut != username:
                username = ut
                request.session['username_session'] = username
            try:
                # 删除该用户的权限信息
                del request.session['user_permission']
            except Exception as e:
                pass
            # 如果用户存在，则根据用户查角色权限
            # roleId = UserRole.objects.values_list('role_id', flat=True).filter(user_id=user.id)
            user = User.objects.get(username=username)
            roleId = user.roles.values_list('id', flat=True).all()
            user_permission = Permission.objects.filter(role_id__in=list(roleId)).values_list('module__optValue')
            permission_session = request.session.get('user_permission')
            if permission_session is None:
                request.session['user_permission'] = list(user_permission)
                request.session.set_expiry(0)


def permission_required(permission):
    """自定义views的权限校验装饰器"""

    def decorator(func):
        def warpper(request, *args, **kwargs):
            if not request.session['user_permission'] or permission not in request.session['user_permission']:
                # return JsonResponse({'code': 400, 'msg': '无权操作'})
                raise CustomSystemException(msg='您无权操作')
            else:
                return func(request, *args, **kwargs)

        return warpper

    return decorator
