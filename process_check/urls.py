from django.urls import path

from . import views

app_name = 'process_check'
urlpatterns = [
    # ex: /process_check/
    path('', views.server_list, name='process_check'),
    path('server_list_left_ajax', views.server_list_left_ajax, name='server_list_left_ajax'),
    path('server_list_reload_left_ajax', views.server_list_reload_left_ajax, name='server_list_reload_left_ajax'),
    path('server_list_right_ajax', views.server_list_right_ajax, name='server_list_right_ajax'),
    
]