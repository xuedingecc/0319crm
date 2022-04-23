from django.urls import path
from system import views

app_name = 'system'

urlpatterns = [
    path('login_register/', views.login_register, name='login_register'),
    path('unique_username/', views.unique_username, name='unique_username'),
    path('unique_email/', views.unique_email, name='unique_email'),
    path('send_email/', views.send_email, name='send_email'),
    path('active_account/', views.active_account, name='active_account'),
    path('login_user/', views.login_user, name='login_user'),
    path('index/', views.index, name='index'),
    path('update_password/', views.update_password, name='update_password'),
    path('logout/', views.logout, name='logout'),
    path('select_customer_manager/', views.select_customer_manager, name='select_customer_manager'),
    path('module_index/', views.module_index, name='module_index'),
    path('select_module_by_grade/', views.select_module_by_grade, name='select_module_by_grade'),
    path('update_module/', views.update_module, name='update_module'),
    path('select_module/', views.select_module, name='select_module'),
    path('create_module/', views.create_module, name='create_module'),
    path('delete_module/', views.delete_module, name='delete_module'),
    path('role_index/', views.role_index, name='role_index'),
    path('update_role/', views.update_role, name='update_role'),
    path('select_role/', views.select_role, name='select_role'),
    path('create_role/', views.create_role, name='create_role'),
    path('delete_role/', views.delete_role, name='delete_role'),
    path('role_module_index/', views.role_module_index, name='role_module_index'),
    path('role_relate_module/', views.role_relate_module, name='role_relate_module'),
    path('role_relate_module/', views.role_relate_module, name='role_relate_module'),
    path('user_index/', views.user_index, name='user_index'),
    path('select_user/', views.select_user, name='select_user'),
    path('select_role_for_user/', views.select_role_for_user, name='select_role_for_user'),
    path('create_user/', views.create_user, name='create_user'),
    path('select_role_by_userid/', views.select_role_by_userid, name='select_role_by_userid'),
    path('update_user/', views.update_user, name='update_user'),
    path('delete_user/', views.delete_user, name='delete_user'),
]
