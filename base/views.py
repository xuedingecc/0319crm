from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from base.models import DataDic, Product
from datetime import datetime
from django.db.models import Count


@require_GET
def select_customer_level(request):
    try:
        dic_name = request.GET.get('dic_name')
        res = DataDic.objects.values('dataDicValue').filter(dataDicName=dic_name)
        return JsonResponse(list(res), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


def datadic_index(request):
    return render(request, 'base/datadic_index.html')


@require_GET
def select_datadic(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        ones = DataDic.objects.values().order_by('-dataDicName')
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '查询失败'})


@require_GET
def select_datadic_name(request):
    try:
        # ones = DataDic.objects.values('dataDicName').annotate(dn=Count('dataDicName'))
        ones = DataDic.objects.values('dataDicName').distinct()
        return JsonResponse(list(ones), safe=False)
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def create_datadic(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        data.pop('id')
        DataDic.objects.create(**data)
        return JsonResponse({"code": 200, 'msg': '创建成功'})

    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '创建失败'})


@csrf_exempt
@require_POST
def update_datadic(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        DataDic.objects.filter(pk=id).update(**data)
        return JsonResponse({"code": 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '更新失败'})


@require_GET
def delete_datadic(request):
    try:
        ids = request.GET.get('id')
        ids = ids.split(',')
        DataDic.objects.filter(pk__in=ids).update(isValid=0, updateDate=datetime.now())
        # for id in ids:
        # DataDic.objects.filter(pk=int(id)).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({"code": 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '删除失败'})


def product_index(request):
    return render(request, 'base/product_index.html')


@require_GET
def select_product(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        ones = Product.objects.values().order_by('-id')
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '查询失败'})


# @require_GET
# def select_product_name(request):
#     try:
#         # ones = DataDic.objects.values('dataDicName').annotate(dn=Count('dataDicName'))
#         ones = DataDic.objects.values('dataDicName').distinct()
#         return JsonResponse(list(ones), safe=False)
#     except Exception as e:
#         return JsonResponse({"code": 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def create_product(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        data.pop('id')
        Product.objects.create(**data)
        return JsonResponse({"code": 200, 'msg': '创建成功'})

    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '创建失败'})


@csrf_exempt
@require_POST
def update_product(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        Product.objects.filter(pk=id).update(**data)
        return JsonResponse({"code": 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '更新失败'})


@require_GET
def delete_product(request):
    try:
        ids = request.GET.get('id')
        ids = ids.split(',')
        Product.objects.filter(pk__in=ids).update(isValid=0, updateDate=datetime.now())
        # for id in ids:
        # DataDic.objects.filter(pk=int(id)).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({"code": 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '删除失败'})
