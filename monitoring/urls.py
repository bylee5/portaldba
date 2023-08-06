from django.urls import path

from . import views

app_name = 'monitoring'
urlpatterns = [
    # ex: /monitoring/
    path('', views.monitoring, name='monitoring'),
    path('threads_connected/', views.threads_connected, name='threads_connected'),
    path('threads_running/', views.threads_running, name='threads_running'),
    path('slave_delay/', views.slave_delay, name='slave_delay'),
    path('innodb_lock/', views.innodb_lock, name='innodb_lock'),
    path('slow_query/', views.slow_query, name='slow_query'),
    path('undo_size/', views.undo_size, name='undo_size'),
]