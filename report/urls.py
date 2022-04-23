from django.urls import path, include
from report import views

app_name = 'report'

urlpatterns = [
    path('report_index/<str:rr>/', views.report_index, name='report_index'),
    path('select_contirbute/', views.select_contirbute, name='select_contirbute'),
    path('select_compostion/', views.select_compostion, name='select_compostion'),
    path('select_serve/', views.select_serve, name='select_serve')
]
