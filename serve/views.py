from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from datetime import datetime

from .models import CustomerServe


@require_GET
def serve_index(request, serve_type):
    return render(request, 'serve/serve_{}.html'.format(serve_type))


@csrf_exempt
@require_POST
def create_serve(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        data['state'] = '新创建'
        data['createPeople'] = request.session.get('username_session')
        CustomerServe.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '创建成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '创建失败'})


# def serve_assign(request):
#     return render(request, 'serve/serve_assign.html')
#
#
# def serve_handler(request):
#     return render(request, 'serve/serve_handler.html')
#
#
# def serve_feedback(request):
#     return render(request, 'serve/serve_feedback.html')
#
#
# def serve_file(request):
#     return render(request, 'serve/serve_file.html')


@require_GET
def select_serve(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')

        customer = request.GET.get('customer')
        overview = request.GET.get('overview')
        serveType = request.GET.get('serveType')
        createTimefrom = request.GET.get('createTimefrom')
        createDateto = request.GET.get('createDateto')

        state = request.GET.get('state')

        ones = CustomerServe.objects.values().filter(state=state).order_by('-id')

        if customer:
            ones = ones.filter(customer__contains=customer)
        if overview:
            ones = ones.filter(overview__contains=overview)
        if serveType and '请选择服务类型' != serveType:
            ones = ones.filter(serveType=serveType)
        if createTimefrom:
            ones = ones.filter(createDate__gte=createTimefrom)
        if createDateto:
            ones = ones.filter(createDate__lte=createDateto)

        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def update_serve(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        id = data.pop('id')
        state = data['state']
        if state == '已分配':
            data['assignTime'] = datetime.now()
        if state == '已处理':
            data['serviceProceTime'] = datetime.now()
        data['updateDate'] = datetime.now()
        CustomerServe.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})
