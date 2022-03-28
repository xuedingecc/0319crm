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
    path('logout/', views.logout, name='logout')
]
