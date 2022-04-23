from django.urls import path
from sales import views

app_name = 'sales'

urlpatterns = [
    path('sale_chance_index/', views.sale_chance_index, name='sale_chance_index'),
    path('select_sale_chance_list/', views.select_sale_chance_list, name='select_sale_chance_list'),
    path('create_sale_chance/', views.create_sale_chance, name='create_sale_chance'),
    path('update_sale_chance/', views.update_sale_chance, name='update_sale_chance'),
    path('select_sale_chance_by_id/', views.select_sale_chance_by_id, name='select_sale_chance_by_id'),
    path('delete_sale_chance/', views.delete_sale_chance, name='delete_sale_chance'),
    path('cus_dev_plan_index/', views.cus_dev_plan_index, name='cus_dev_plan_index'),
    path('select_cus_dev_plan_list/', views.select_cus_dev_plan_list, name='select_cus_dev_plan_list'),
    path('select_sale_chance_by_id_for_page/', views.select_sale_chance_by_id_for_page,
         name='select_sale_chance_by_id_for_page'),
    path('select_cus_dev_plan_by_sale_chance_id/<int:sale_chance_id>/', views.select_cus_dev_plan_by_sale_chance_id,
         name='select_cus_dev_plan_by_sale_chance_id'),
    path('create_cus_dev_plan/<int:sale_chance_id>/', views.create_cus_dev_plan, name='create_cus_dev_plan'),
    path('update_cus_dev_plan/', views.update_cus_dev_plan, name='update_cus_dev_plan'),
    path('delete_cus_dev_plan/', views.delete_cus_dev_plan, name='delete_cus_dev_plan'),
    path('update_dev_result/', views.update_dev_result, name='update_dev_result')
]
