from django.urls import path
from system import views

app_name = 'system'

urlpatterns = [
    path('login_register/', views.login_register, name='login_register')
]
