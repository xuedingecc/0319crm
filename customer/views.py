from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from crm.common import permission_required
from customer.models import Customer, LinkMan, Contact, CustomerOrders, OrdersDetail, CustomerLoss, CustomerReprieve
from system.models import User
from django.shortcuts import render
from django.core.paginator import Paginator

from datetime import datetime
import random


@require_GET
@permission_required('101001')
def select_cname_and_lname_and_uname(request):
    try:
        us = User.objects.values('id', 'username').all()
        cs = Customer.objects.values('id', 'name').all()
        ls = LinkMan.objects.values('id', 'linkName').all()
        context = {
            'code': 200,
            'cs': list(cs),
            'ls': list(ls),
            'us': list(us)
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '打开失败'})


@require_GET
def select_link_phone_by_id(request):
    try:
        id = request.GET.get('id')
        cus = Customer.objects.values('phone').get(id=id)
        return JsonResponse({'code': 200, 'phone': cus['phone']})
    except Customer.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '用戶不存在'})


def customer_index(request):
    return render(request, 'customer/customer.html')


@require_GET
def select_customer_list(request):
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('rows')
        name = request.GET.get('name')
        khno = request.GET.get('khno')
        state = request.GET.get('state')
        ones = Customer.objects.all().values()
        if name:
            ones = ones.filter(name__contains=name)
        if khno:
            ones = ones.filter(khno__contains=khno)
        if state:
            ones = ones.filter(state=state)
        p = Paginator(list(ones), page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': data
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def create_customer(request):
    try:
        data = request.POST.dict()
        # 生成客户编号
        data['khno'] = 'HK' + datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))
        Customer.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


@require_GET
def select_customer_by_id(request):
    try:
        id = request.GET.get('id')
        one = Customer.objects.values().get(pk=id)
        return JsonResponse({'code': 200, 'obj': one})
    except Customer.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '查找失败'})


# @csrf_exempt
@require_POST
def update_customer(request):
    try:
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        Customer.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@require_GET
def delete_customer(request):
    try:
        ids = request.GET.get('ids')
        for id in ids.split(','):
            Customer.objects.filter(pk=id).update(isValid=0)
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@require_GET
def linkman_index(request):
    try:
        id = request.GET.get('id')
        one = Customer.objects.values('id', 'khno', 'name').get(id=id)
        return render(request, 'customer/linkman.html', {'c': one})
    except Customer.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '查找失败'})


@csrf_exempt
@require_POST
def select_linkman_by_customer_id(request, id):
    try:
        page_num = request.POST.get('page')
        page_size = request.POST.get('rows')
        object_list = LinkMan.objects.values().filter(customer_id=id).order_by('-id')
        p = Paginator(object_list, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except LinkMan.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '查找失败'})


@csrf_exempt
@require_POST
def create_linkman(request, id):
    try:
        data = request.POST.dict()
        data.pop('isNewRecord')
        c = Customer.objects.get(pk=id)
        data['customer'] = c
        LinkMan.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '创建成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '创建失败'})


@csrf_exempt
@require_POST
def update_linkman(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        LinkMan.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@csrf_exempt
@require_POST
def delete_linkman(request):
    try:
        id = request.POST.get('id')
        LinkMan.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@require_GET
def contact_index(request):
    try:
        id = request.GET.get('id')
        one = Customer.objects.values('id', 'khno', 'name').get(pk=id)
        return render(request, 'customer/contact.html', {'c': one})
    except Customer.DoesNotExist as e:
        return JsonResponse({'code': 400, 'msg': '查找失败'})


@csrf_exempt
@require_POST
def select_contact_by_customer_id(request, id):
    try:
        page_num = request.POST.get('page')
        page_size = request.POST.get('rows')
        ones = Contact.objects.values().filter(customer_id=id).order_by('-id')
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
def create_contact(request, id):
    try:
        data = request.POST.dict()
        data.pop('isNewRecord')
        c = Customer.objects.get(pk=id)
        data['customer'] = c
        print(data)
        Contact.objects.create(**data)
        return JsonResponse({'code': 200, 'msg': '创建成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '创建失败'})


@csrf_exempt
@require_POST
def update_contact(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        Contact.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@csrf_exempt
@require_POST
def delete_contact(request):
    try:
        id = request.POST.get('id')
        Contact.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@require_GET
def order_index(request):
    id = request.GET.get('id')
    c = Customer.objects.values('id', 'name', 'khno').get(pk=id)
    return render(request, 'customer/order.html', {'c': c})


@csrf_exempt
@require_POST
def select_order_by_customer_id(request, id):
    try:
        page_num = request.POST.get('page')
        page_size = request.POST.get('rows')
        ones = CustomerOrders.objects.values().filter(customer_id=id).order_by('-id')
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
def select_order_by_id(request):
    try:
        id = request.GET.get('order_id')
        one = CustomerOrders.objects.values().get(pk=id)
        return JsonResponse({'code': 200, 'obj': one})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def select_order_detail_by_order_id(request, id):
    try:
        page_num = request.POST.get('page')  # 第几页
        page_size = request.POST.get('rows')  # 每页多少个
        ones = OrdersDetail.objects.values().filter(order_id=id).order_by('-id')
        p = Paginator(ones, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


def customer_loss_index(request):
    return render(request, 'customer/loss.html')


@require_GET
def select_loss(reqeust):
    try:
        cusName = reqeust.GET.get('cusName')
        cusManager = reqeust.GET.get('cusManager')
        state = reqeust.GET.get('state')
        page_num = reqeust.GET.get('page')
        page_size = reqeust.GET.get('rows')
        ones = CustomerLoss.objects.values().all().order_by('-id')
        if cusName:
            ones = ones.filter(cusName__contains=cusName)
        if cusManager:
            ones = ones.filter(cusManager__contains=cusManager)
        if state:
            ones = ones.filter(state=state)
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
def reprieve_index(request):
    try:
        id = request.GET.get('id')
        cl = CustomerLoss.objects.values().get(pk=id)
        return render(request, 'customer/reprieve.html', {'cl': cl})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


@csrf_exempt
@require_POST
def select_reprieve_by_loss_id(request, id):
    try:
        page_num = request.POST.get('page')
        page_size = request.POST.get('rows')
        ones = CustomerReprieve.objects.values().filter(customerLoss__id=id).order_by('-id')

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
def create_reprieve(request, id):
    try:
        data = request.POST.dict()
        data.pop('isNewRecord')
        cl = CustomerLoss.objects.get(pk=id)
        data['customerLoss'] = cl
        CustomerReprieve.objects.create(**data)
        return JsonResponse({'code': 400, 'msg': '创建成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '创建失败'})


@csrf_exempt
@require_POST
def update_reprieve(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        CustomerReprieve.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 400, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


@csrf_exempt
@require_POST
def delete_reprieve(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['isValid'] = 0
        data['updateDate'] = datetime.now()
        CustomerReprieve.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 400, 'msg': '刪除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


@csrf_exempt
@require_POST
def ok_reprieve(request):
    try:
        loss_id = request.POST.get('loss_id')
        lossReason = request.POST.get('lossReason')
        CustomerLoss.objects.filter(pk=loss_id).update(state=1, lossReason=lossReason, confirmLossTime=datetime.now(),
                                                       updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': '流失成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '流失失败'})


@require_GET
def select_customer_name(reqeust):
    try:
        ones = Customer.objects.values('name').all()
        return JsonResponse(list(ones), safe=False)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})
