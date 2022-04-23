from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from customer.models import Customer, CustomerOrders
from serve.models import CustomerServe
from django.db.models import Sum, F, Count


def report_index(request, rr):
    print(rr)
    return render(request, 'report/{}.html'.format(rr))


@require_GET
def select_contirbute(request):
    try:
        name = request.GET.get('name')
        page_sum = request.GET.get('page')
        page_size = request.GET.get('rows')

        ones = CustomerOrders.objects.values('customer__name').annotate(name=F('customer__name'),
                                                                        sum=Sum('totalPrice')).order_by(
            'customer__name')
        if name:
            ones = ones.filter(name__contains=name)
        # 打印sql
        print(ones.query)
        p = Paginator(ones, page_size)
        data = p.page(page_sum).object_list
        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@require_GET
def select_compostion(request):
    try:
        datas = Customer.objects.values('level').annotate(amount=Count('level'))
        return JsonResponse(list(datas), safe=False)
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '查询失败'})


@require_GET
def select_serve(request):
    try:
        datas = CustomerServe.objects.values('serveType').annotate(amount=Count('serveType'))
        return JsonResponse(list(datas), safe=False)
    except Exception as e:
        return JsonResponse({"code": 400, 'msg': '查询失败'})
