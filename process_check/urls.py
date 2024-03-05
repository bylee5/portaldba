from django.urls import path

from . import views

app_name = 'process_check'
urlpatterns = [
    # ex: /process_check/
    path('', views.server_list, name='server_list'),
    path('server_list_left_ajax', views.server_list_left_ajax, name='server_list_left_ajax'),
    path('server_list_reload_left_ajax', views.server_list_reload_left_ajax, name='server_list_reload_left_ajax'),
    path('server_list_right_ajax', views.server_list_right_ajax, name='server_list_right_ajax'),
    path('server_list_delete_svr_use_yn_ajax', views.server_list_delete_svr_use_yn_ajax, name='server_list_delete_svr_use_yn_ajax'),
    path('server_list_update_svr_use_yn_ajax', views.server_list_update_svr_use_yn_ajax, name='server_list_update_svr_use_yn_ajax'),

]