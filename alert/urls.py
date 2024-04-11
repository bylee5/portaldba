from django.urls import path

from . import views

app_name = 'alert'
urlpatterns = [
    # ex: /alert/
    path('', views.alert, name='alert'),
    path('alert_select', views.alert_select, name='alert_select'),
    path('alert_insert', views.alert_insert, name='alert_insert'),
    path('alert_multi_dml', views.alert_multi_dml, name='alert_multi_dml'),
    path('alert_delete', views.alert_delete, name='alert_delete'),
    path('alert_update', views.alert_update, name='alert_update'),

    path('alert_remove', views.alert_remove, name='alert_remove'),

    path('alert_add', views.alert_add, name='alert_add'),
    path('alert_add_select', views.alert_add_select, name='alert_add_select'),
    path('alert_add_insert', views.alert_add_insert, name='alert_add_insert'),
    path('alert_add_delete', views.alert_add_delete, name='alert_add_delete'),
    path('alert_add_update', views.alert_add_update, name='alert_add_update'),

    path('threads_connected', views.threads_connected, name='threads_connected'),
    path('threads_connected_select', views.threads_connected_select, name='threads_connected_select'),
    path('threads_running', views.threads_running, name='threads_running'),
    path('threads_running_select', views.threads_running_select, name='threads_running_select'),
    path('slave_delay', views.slave_delay, name='slave_delay'),
    path('slave_delay_select', views.slave_delay_select, name='slave_delay_select'),
    path('innodb_lock', views.innodb_lock, name='innodb_lock'),
    path('innodb_lock_select', views.innodb_lock_select, name='innodb_lock_select'),
    path('slow_query', views.slow_query, name='slow_query'),
    path('slow_query_select', views.slow_query_select, name='slow_query_select'),
    path('undo_size', views.undo_size, name='undo_size'),
    path('undo_size_select', views.undo_size_select, name='undo_size_select'),
    path('connection_check', views.connection_check, name='connection_check'),
    path('connection_check_select', views.connection_check_select, name='connection_check_select'),
]