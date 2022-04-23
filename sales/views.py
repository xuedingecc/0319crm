from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from sales.models import SaleChance, CusDevPlan
from django.views.decorators.csrf import csrf_exempt

from crm.common import permission_required
from datetime import datetime
import pymysql

from dbutil import pymysql_pool

# 准备数据
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'db_crm',
    'charset': 'utf8mb4',
    # 默认获取的数据事元组类型，改成字典类型数据
    'cursorclass': pymysql.cursors.DictCursor
}

# 初始化连接池对象
connect_pool = pymysql_pool.ConnectionPool(size=50, name='mysql_pool', **config)


# 从连接池中获取链接
def connect():
    connection = connect_pool.get_connection()
    return connection


# 跳转营销机会
def sale_chance_index(request):
    return render(request, 'sales/sale_chacne.html')


# 查询营销机会
@require_GET
def select_sale_chance_list(request):
    '''查所有营销机会'''
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('rows')

        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        sql = '''
            SELECT
                sc.id id,# 主键
                c.id customerId,# 客户表主键
                c.khno khno,# 客户编号
                c.name customerName,# 客户名称
                sc.overview overview,# 概要
                sc.create_man createMan,# 创建人
                cl.id linkManId,# 联系人主键
                cl.link_name linkManName,# 联系人姓名
                cl.phone linkPhone,# 联系电话
                tu.user_name assignMan,# 指派人名称
                sc.assign_time assignTime,# 指派时间
                sc.state state,# 分配状态
                sc.dev_result devResult # 开发状态
            FROM
                t_sale_chance sc
            LEFT JOIN t_customer c ON sc.customer_id = c.id 
            LEFT JOIN t_customer_linkman cl ON sc.link_man = cl.id
            LEFT JOIN t_user tu ON sc.assign_man = tu.id
            WHERE 1=1 AND sc.is_valid = 1
        '''
        # 查询参数
        customerName = request.GET.get('customerName')
        overview = request.GET.get('overview')
        createMan = request.GET.get('createMan')
        state = request.GET.get('state')

        if customerName:
            sql += ' AND c.name like "%{}%" '.format(customerName)

        if overview:
            sql += 'AND sc.overview like "%{}%"'.format(overview)

        if createMan:
            sql += 'AND sc.create_man like "%{}%"'.format(createMan)

        if state:
            sql += 'AND sc.state = {}'.format(state)

        sql += ' ORDER BY sc.id DESC;'

        # 执行sql
        cursor.execute(sql)

        # 返回多条结果行
        object_list = cursor.fetchall()  # 查询当前sql执行后的所有记录

        # 关闭游标
        cursor.close()

        p = Paginator(object_list, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': data
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400})
    finally:
        connection.close()


# 添加营销机会
@require_POST
@permission_required('101001')
def create_sale_chance(request):
    # 从session中获取用户的权限值
    # user_permission = request.session.get['user_permission']
    # if '101001' not in user_permission:
    #     return JsonResponse({'code': 400, 'msg': '没有权限操作'})
    try:
        customerId = request.POST.get('customerId').strip()
        customerName = request.POST.get('customerName_hidden').strip()
        chanceSource = request.POST.get('chanceSource').strip()
        linkId = request.POST.get('linkManId').strip()
        linkPhone = request.POST.get('linkPhone').strip()
        cgjl = request.POST.get('cgjl').strip()
        overview = request.POST.get('overview').strip()
        description = request.POST.get('description').strip()
        assignMan = request.POST.get('assignMan').strip()

        if assignMan is not '0':
            sc = SaleChance(customerId=customerId, customerName=customerName, chanceSource=chanceSource, linkMan=linkId,
                            linkPhone=linkPhone, cgjl=cgjl, overview=overview, description=description,
                            createMan=request.session['username_session'], assignMan=assignMan,
                            assignTime=datetime.now(), state=1)
        else:
            sc = SaleChance(customerId=customerId, customerName=customerName, chanceSource=chanceSource, linkMan=linkId,
                            linkPhone=linkPhone, cgjl=cgjl, overview=overview, description=description,
                            createMan=request.session['username_session'], state=0)
        sc.save()
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失敗'})


# 根据id查询营销机会
@require_GET
def select_sale_chance_by_id(request):
    try:
        id = request.GET.get('id')

        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        sql = '''
            SELECT
                sc.id id,# 主键
                c.id customerId,# 客户表主键
                c.name customerName,# 客户名称11
                sc.chance_source chanceSource, #机会来源
                sc.overview overview,# 概要11
                sc.create_man createMan,# 创建人
                sc.link_man linkMan,# 联系人主键11
                cl.phone linkPhone,# 联系电话11
                sc.assign_man assignMan,# 指派人名称11
                sc.cgjl cgjl, #成功几率
                sc.description description #机会描述
            FROM
                t_sale_chance sc
            LEFT JOIN t_customer c ON sc.customer_id = c.id 
            LEFT JOIN t_customer_linkman cl ON sc.link_man = cl.id
            LEFT JOIN t_user tu ON sc.assign_man = tu.id
            WHERE 1=1 AND sc.id = %s
        '''
        # 执行sql
        cursor.execute(sql, (id,))

        # 返回多条结果行
        one = cursor.fetchone()  # 查询当前sql执行后的所有记录

        # 关闭游标
        cursor.close()

        return JsonResponse({'code': 200, 'sc': one})
    except SaleChance.DoesNotExist:
        return JsonResponse({'code': 400, 'msg': '查詢錯誤'})
    finally:
        connection.close()


# 更新营销机会
@csrf_exempt
@require_POST
def update_sale_chance(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        if data['assignMan'] == '0':
            data['assignTime'] = None
            data['state'] = 0
        else:
            data['state'] = 1
            data['assignTime'] = datetime.now()
        SaleChance.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


# 删除营销机会
@csrf_exempt
@require_POST
def delete_sale_chance(request):
    try:
        ids = request.POST.get('ids')
        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        # sql = 'DELETE FROM t_sale_chance WHERE id IN (%s);'
        ids = ids.split(',')
        for id in ids:
            sql = 'UPDATE t_sale_chance SET is_valid = 0 WHERE id = %s;'
            # 执行sql
            cursor.execute(sql, (id,))
        # 提交
        connection.commit()
        # 关闭游标
        cursor.close()

        return JsonResponse({'code': 200, 'msg': '删除成功'})

    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})
    finally:
        connection.close()


# 跳转客户开发计划
def cus_dev_plan_index(request):
    return render(request, 'sales/cus_dev_plan.html')


# 查询客户开发计划
@require_GET
def select_cus_dev_plan_list(request):
    '''查所有营销机会'''
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('rows')

        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        sql = '''
            SELECT
                sc.id id,# 主键
                c.id customerId,# 客户表主键
                c.khno khno,# 客户编号1
                c.name customerName,# 客户名称1
                sc.overview overview,# 概要1
                sc.create_man createMan,# 创建人1
                cl.id linkManId,# 联系人主键
                cl.link_name linkManName,# 联系人姓名1
                cl.phone linkPhone,# 联系电话1
                tu.user_name assignMan,# 指派人名称1
                sc.assign_time assignTime,# 指派时间1
                sc.state state,# 分配状态
                sc.dev_result devResult # 开发状态
            FROM
                t_sale_chance sc
            LEFT JOIN t_customer c ON sc.customer_id = c.id 
            LEFT JOIN t_customer_linkman cl ON sc.link_man = cl.id
            LEFT JOIN t_user tu ON sc.assign_man = tu.id
            WHERE 1=1 AND sc.is_valid = 1 AND sc.state = 1
        '''
        # 查询参数
        customerName = request.GET.get('customerName')
        overview = request.GET.get('overview')
        devResult = request.GET.get('devResult')

        if customerName:
            sql += ' AND c.name like "%{}%" '.format(customerName)

        if overview:
            sql += 'AND sc.overview like "%{}%"'.format(overview)

        if devResult:
            sql += 'AND sc.dev_result = {}'.format(devResult)

        sql += ' ORDER BY sc.id DESC;'

        # 执行sql
        cursor.execute(sql)

        # 返回多条结果行
        object_list = cursor.fetchall()  # 查询当前sql执行后的所有记录

        # 关闭游标
        cursor.close()

        p = Paginator(object_list, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': data
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400})
    finally:
        connection.close()


# 打开营销机会
@require_GET
def select_sale_chance_by_id_for_page(request):
    try:
        id = request.GET.get('sale_chance_id')
        flag = request.GET.get('flag')

        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        sql = '''
            SELECT
                sc.id id,# 主键
                c.id customerId,# 客户表主键
                c.khno khno,# 客户编号1
                c.name customerName,# 客户名称1
                sc.overview overview,# 概要1
                sc.chance_source chanceSource,# 机会来源
                sc.cgjl cgjl,# 成功几率
                sc.description description,# 机会描述
                sc.create_man createMan,# 创建人1
                cl.id linkManId,# 联系人主键
                cl.link_name linkManName,# 联系人姓名1
                cl.phone linkPhone,# 联系电话1
                tu.user_name assignMan,# 指派人名称1
                sc.assign_time assignTime,# 指派时间1
                sc.create_date createDate,# 创建时间
                sc.state state,# 分配状态
                sc.dev_result devResult # 开发状态
            FROM
                t_sale_chance sc
            LEFT JOIN t_customer c ON sc.customer_id = c.id 
            LEFT JOIN t_customer_linkman cl ON sc.link_man = cl.id
            LEFT JOIN t_user tu ON sc.assign_man = tu.id
            WHERE 1=1 AND sc.id = %s
        '''
        # 执行sql
        cursor.execute(sql, (id,))

        # 返回多条结果行
        one = cursor.fetchone()  # 查询当前sql执行后的所有记录

        # 关闭游标
        cursor.close()

        return render(request, 'sales/cus_dev_plan_detail.html', {'code': 200, 'sc': one, 'flag': flag})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


# 查看开发计划
@csrf_exempt
@require_POST
def select_cus_dev_plan_by_sale_chance_id(request, sale_chance_id):
    try:
        # 获取第几页
        page_num = request.POST.get('page')
        # 获取每页多少条
        page_size = request.POST.get('rows')

        # 获取链接
        connection = connect()
        # 创建游标对象
        cursor = connection.cursor()

        # 编写sql
        sql = '''
            SELECT
            	cdp.id id,
                cdp.plan_item planItem,
                cdp.plan_date planDate,
                cdp.exe_affect exeAffect
            FROM
                t_cus_dev_plan cdp
            WHERE 1=1 AND cdp.is_valid = 1 AND cdp.sale_chance_id = %s
        '''

        cursor.execute(sql, (sale_chance_id,))

        # 返回多条结果行
        object_list = cursor.fetchall()  # 查询当前sql执行后的所有记录

        # 关闭游标
        cursor.close()

        p = Paginator(object_list, page_size)
        data = p.page(page_num).object_list

        context = {
            'total': p.count,
            'rows': data
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '查询失败'})


# 添加开发计划
@csrf_exempt
@require_POST
def create_cus_dev_plan(request, sale_chance_id):
    try:
        data = request.POST.dict()
        data.pop('isNewRecord')
        sc = SaleChance.objects.get(pk=sale_chance_id)
        data['saleChance'] = sc
        CusDevPlan.objects.create(**data)
        # 营销机会变成开发中
        SaleChance.objects.filter(pk=sale_chance_id).update(devResult=1)
        return JsonResponse({'code': 200, 'msg': '添加成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '添加失败'})


# 更改开发计划
@csrf_exempt
@require_POST
def update_cus_dev_plan(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        data['updateDate'] = datetime.now()
        CusDevPlan.objects.filter(pk=id).update(**data)
        return JsonResponse({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '更新失败'})


# 删除开发计划
@csrf_exempt
@require_POST
def delete_cus_dev_plan(request):
    try:
        data = request.POST.dict()
        id = data.pop('id')
        CusDevPlan.objects.filter(pk=id).update(isValid=0)
        return JsonResponse({'code': 200, 'msg': '刪除成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '删除失败'})


# 更改开发状态
@require_GET
def update_dev_result(request):
    try:
        dev_result = request.GET.get('dev_result')
        sale_chance_id = request.GET.get('sale_chance_id')
        SaleChance.objects.filter(pk=sale_chance_id).update(devResult=dev_result)
        return JsonResponse({'code': 200, 'msg': '修改成功'})
    except Exception as e:
        return JsonResponse({'code': 400, 'msg': '修改失败'})
