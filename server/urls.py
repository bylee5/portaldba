from django.urls import path

from . import views

app_name = 'server'
urlpatterns = [
    # ex: /server/
    path('', views.server, name='server'),
    path('select', views.server_select, name='server_select'),
    path('dummy', views.server_dummy, name='server_dummy'),
    path('insert', views.server_insert, name='server_insert'),
    path('delete', views.server_delete, name='server_delete'),
    path('update', views.server_update, name='server_update'),
    path('multi_dml', views.server_multi_dml, name='server_multi_dml'),
    
    # 서버 삭제이력
    path('server_remove', views.server_remove, name='server_remove'),
    path('server_remove_select', views.server_remove_select, name='server_remove_select'),
]