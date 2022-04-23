from django.urls import path
from serve import views

app_name = 'serve'

urlpatterns = [
    path('serve_index/<str:serve_type>/', views.serve_index, name='serve_index'),
    # path('serve_assign/', views.serve_assign, name='serve_assign'),
    # path('serve_handler/', views.serve_handler, name='serve_handler'),
    # path('serve_feedback/', views.serve_feedback, name='serve_feedback'),
    # path('serve_file/', views.serve_file, name='serve_file'),
    path('create_serve/', views.create_serve, name='create_serve'),
    path('select_serve/', views.select_serve, name='select_serve'),
    path('update_serve/', views.update_serve, name='update_serve'),
]
