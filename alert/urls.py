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
    path('threads_running', views.threads_running, name='threads_running'),
    path('slave_delay', views.slave_delay, name='slave_delay'),
    path('innodb_lock', views.innodb_lock, name='innodb_lock'),
    path('slow_query', views.slow_query, name='slow_query'),
    path('undo_size', views.undo_size, name='undo_size'),
]